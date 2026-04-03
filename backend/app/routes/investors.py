from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import FundingRound, InvestmentCommitment, InvestorInterest, Startup, User
from ..utils import create_notification, error_response, get_startup_ids_for_user, log_activity, recalculate_startup_totals, refresh_startup_visibility, role_required, startup_accepting_investment

investors_bp = Blueprint("investors", __name__)


def _commitment_round_name(commitment):
    return f"Commitment {commitment.id}"


def _get_commitment_funding_round(commitment):
    return FundingRound.query.filter_by(
        startup_id=commitment.startup_id,
        lead_investor_id=commitment.investor_id,
        round_name=_commitment_round_name(commitment),
    ).first()


def _sync_commitment_funding_round(commitment, actor_user_id):
    round_date = (commitment.agreed_at or datetime.utcnow()).date()
    funding_round = _get_commitment_funding_round(commitment)
    if funding_round is None:
        funding_round = FundingRound(
            startup_id=commitment.startup_id,
            round_name=_commitment_round_name(commitment),
            round_type=commitment.startup.funding_stage or "Commitment",
            amount_raised=commitment.approved_amount or commitment.requested_amount,
            equity_percentage=commitment.equity_percentage,
            mou_status="SIGNED",
            round_status="CLOSED",
            lead_investor_id=commitment.investor_id,
            announced_on=round_date,
            closed_on=round_date,
            created_by=actor_user_id,
            investment_requirements=commitment.startup_requirements,
        )
        db.session.add(funding_round)
        db.session.flush()
        log_activity(actor_user_id, "funding_round", funding_round.id, "CREATE", f"Created funding round {funding_round.round_name} from interest approval")
        return funding_round

    funding_round.round_type = commitment.startup.funding_stage or funding_round.round_type
    funding_round.amount_raised = commitment.approved_amount or commitment.requested_amount
    funding_round.equity_percentage = commitment.equity_percentage
    funding_round.mou_status = "SIGNED"
    funding_round.round_status = "CLOSED"
    funding_round.announced_on = funding_round.announced_on or round_date
    funding_round.closed_on = round_date
    funding_round.investment_requirements = commitment.startup_requirements
    log_activity(actor_user_id, "funding_round", funding_round.id, "UPDATE", f"Updated funding round {funding_round.round_name} from interest approval")
    return funding_round


def _remove_commitment_funding_round(commitment, actor_user_id):
    funding_round = _get_commitment_funding_round(commitment)
    if funding_round is None:
        return
    log_activity(actor_user_id, "funding_round", funding_round.id, "DELETE", f"Removed funding round {funding_round.round_name} after interest rejection")
    db.session.delete(funding_round)


@investors_bp.post("/interest")
@jwt_required()
@role_required("INVESTOR")
def express_interest():
    data = request.get_json() or {}
    startup_id = data.get("startupId")
    requested_amount = data.get("requestedAmount")
    equity_percentage = data.get("equityPercentage")
    if not startup_id or requested_amount in (None, "") or equity_percentage in (None, ""):
        return error_response("startupId, requestedAmount, and equityPercentage are required", 400)

    try:
        requested_amount = float(requested_amount)
        equity_percentage = float(equity_percentage)
    except (TypeError, ValueError):
        return error_response("requestedAmount and equityPercentage must be valid numbers", 400)

    if requested_amount < 0:
        return error_response("requestedAmount must be greater than or equal to 0", 400)
    if equity_percentage < 0 or equity_percentage > 100:
        return error_response("equityPercentage must be between 0 and 100", 400)

    startup = Startup.query.get_or_404(startup_id)
    if not startup_accepting_investment(startup):
        return error_response("Startup is not currently accepting investment", 400)

    investor_id = int(get_jwt_identity())

    approved_other = sum(item.equity_percentage for item in startup.commitments if item.status == "APPROVED")
    if approved_other + equity_percentage > 100:
        return error_response("Total equity percentage cannot exceed 100", 400)

    interest = InvestorInterest(
        startup_id=startup_id,
        investor_id=investor_id,
        status=data.get("status", "INITIATED"),
        pipeline_stage=data.get("pipelineStage", "OFFER_SUBMITTED"),
        notes=data.get("notes") or data.get("investorNotes"),
    )
    db.session.add(interest)
    db.session.flush()

    commitment = InvestmentCommitment(
        startup_id=startup_id,
        investor_id=investor_id,
        interest_id=interest.id,
        requested_amount=requested_amount,
        equity_percentage=equity_percentage,
        startup_requirements=data.get("startupRequirements") or startup.funding_requirements,
        investor_notes=data.get("investorNotes"),
    )
    db.session.add(commitment)

    startup_user_ids = [member.user_id for member in startup.members]
    admin_user_ids = [user.id for user in User.query.join(User.role).filter_by(name="ADMIN").all()]
    for recipient_user_id in set(startup_user_ids + admin_user_ids):
        create_notification(
            recipient_user_id,
            "New Investor Interest",
            f"An investor expressed interest in {startup.name}.",
            link=f"/startups/{startup.id}",
        )
    log_activity(investor_id, "investor_interest", interest.id, "CREATE", "Investor expressed interest with offer details")
    log_activity(investor_id, "investment_commitment", commitment.id, "CREATE", "Investor submitted offer details with interest")
    db.session.commit()
    return {"message": "Interest recorded", "interest": interest.to_dict(), "commitment": commitment.to_dict()}, 201


@investors_bp.put("/interest/<int:interest_id>/accept")
@jwt_required()
@role_required("STARTUP_REP")
def accept_interest(interest_id):
    interest = InvestorInterest.query.get_or_404(interest_id)
    user_id = int(get_jwt_identity())
    startup_ids = get_startup_ids_for_user(user_id)
    if interest.startup_id not in startup_ids:
        return error_response("Forbidden", 403)

    commitment = InvestmentCommitment.query.filter_by(interest_id=interest.id, investor_id=interest.investor_id).order_by(InvestmentCommitment.created_at.desc()).first()
    if commitment is None:
        return error_response("No offer is attached to this interest", 400)

    approved_other = sum(
        item.equity_percentage for item in commitment.startup.commitments if item.id != commitment.id and item.status == "APPROVED"
    )
    if approved_other + commitment.equity_percentage > 100:
        return error_response("Total equity percentage cannot exceed 100", 400)

    data = request.get_json() or {}
    interest.status = "ACCEPTED"
    interest.pipeline_stage = data.get("pipelineStage", "STARTUP_ACCEPTED")
    interest.response_notes = data.get("responseNotes")
    interest.responded_by = user_id

    commitment.status = "APPROVED"
    commitment.approved_amount = commitment.requested_amount
    commitment.decision_notes = data.get("responseNotes")
    commitment.decided_by = user_id
    commitment.agreed_at = datetime.utcnow()

    commitment.startup.funding_status = "IN_PROGRESS"
    recalculate_startup_totals(commitment.startup)
    _sync_commitment_funding_round(commitment, user_id)
    refresh_startup_visibility(commitment.startup)

    create_notification(
        interest.investor_id,
        "Interest Accepted",
        f"{interest.startup.name} accepted your offer. You can submit another contribution while the startup remains open.",
        link="/interests",
    )
    stakeholder_ids = {member.user_id for member in interest.startup.members if member.user_id != user_id}
    stakeholder_ids.update(user.id for user in User.query.join(User.role).filter_by(name="ADMIN").all())
    for recipient_user_id in stakeholder_ids:
        create_notification(
            recipient_user_id,
            "Offer Accepted",
            f"{interest.investor.full_name} now has an accepted contribution for {interest.startup.name}.",
            link="/my-startups",
        )
    log_activity(user_id, "investor_interest", interest.id, "UPDATE", "Startup accepted investor interest")
    log_activity(user_id, "investment_commitment", commitment.id, "UPDATE", "Startup approved investor offer")
    db.session.commit()
    return {"message": "Investor interest accepted", "interest": interest.to_dict(), "commitment": commitment.to_dict()}


@investors_bp.put("/interest/<int:interest_id>/reject")
@jwt_required()
@role_required("STARTUP_REP")
def reject_interest(interest_id):
    interest = InvestorInterest.query.get_or_404(interest_id)
    user_id = int(get_jwt_identity())
    startup_ids = get_startup_ids_for_user(user_id)
    if interest.startup_id not in startup_ids:
        return error_response("Forbidden", 403)

    commitment = InvestmentCommitment.query.filter_by(interest_id=interest.id, investor_id=interest.investor_id).order_by(InvestmentCommitment.created_at.desc()).first()

    data = request.get_json() or {}
    interest.status = "REJECTED"
    interest.pipeline_stage = data.get("pipelineStage", "STARTUP_REJECTED")
    interest.response_notes = data.get("responseNotes")
    interest.responded_by = user_id

    if commitment is not None:
        commitment.status = "REJECTED"
        commitment.approved_amount = 0
        commitment.decision_notes = data.get("responseNotes")
        commitment.decided_by = user_id
        _remove_commitment_funding_round(commitment, user_id)
        recalculate_startup_totals(commitment.startup)
        refresh_startup_visibility(commitment.startup)
        log_activity(user_id, "investment_commitment", commitment.id, "UPDATE", "Startup rejected investor offer")

    create_notification(
        interest.investor_id,
        "Investor Interest Rejected",
        f"{interest.startup.name} declined your investor interest.",
        link="/portfolio",
    )
    log_activity(user_id, "investor_interest", interest.id, "UPDATE", "Startup rejected investor interest")
    db.session.commit()
    return {"message": "Investor interest rejected", "interest": interest.to_dict(), "commitment": commitment.to_dict() if commitment else None}


@investors_bp.post("/commitments")
@jwt_required()
@role_required("INVESTOR")
def create_commitment():
    data = request.get_json() or {}
    startup_id = data.get("startupId")
    requested_amount = data.get("requestedAmount")
    equity_percentage = data.get("equityPercentage")
    if not startup_id or requested_amount in (None, "") or equity_percentage in (None, ""):
        return error_response("startupId, requestedAmount, and equityPercentage are required", 400)

    startup = Startup.query.get_or_404(startup_id)
    if not startup_accepting_investment(startup):
        return error_response("Startup is not currently accepting investment", 400)

    investor_id = int(get_jwt_identity())
    interest = InvestorInterest.query.filter_by(startup_id=startup_id, investor_id=investor_id).first()
    if interest and interest.status == "REJECTED":
        return error_response("Your earlier interest was rejected for this startup", 400)

    commitment = InvestmentCommitment(
        startup_id=startup_id,
        investor_id=investor_id,
        interest_id=interest.id if interest else None,
        requested_amount=float(requested_amount),
        equity_percentage=float(equity_percentage),
        startup_requirements=data.get("startupRequirements") or startup.funding_requirements,
        investor_notes=data.get("investorNotes"),
    )
    db.session.add(commitment)
    db.session.flush()

    if interest:
        interest.pipeline_stage = "OFFER_UPDATED"

    recipients = {member.user_id for member in startup.members}
    recipients.update(user.id for user in User.query.join(User.role).filter_by(name="ADMIN").all())
    for recipient_user_id in recipients:
        create_notification(
            recipient_user_id,
            "New Investment Offer",
            f"{commitment.investor.full_name} submitted an updated offer for {startup.name}.",
            link="/my-startups",
        )

    log_activity(investor_id, "investment_commitment", commitment.id, "CREATE", "Investor submitted investment offer")
    db.session.commit()
    return {"message": "Commitment created", "commitment": commitment.to_dict()}, 201


@investors_bp.get("/portfolio")
@jwt_required()
@role_required("INVESTOR")
def portfolio():
    investor_id = int(get_jwt_identity())
    rounds = FundingRound.query.filter(FundingRound.lead_investor_id == investor_id).order_by(FundingRound.created_at.desc()).all()
    commitments = (
        InvestmentCommitment.query.filter_by(investor_id=investor_id)
        .order_by(InvestmentCommitment.created_at.desc())
        .all()
    )
    items = []
    for commitment in commitments:
        item = commitment.to_dict()
        item["startupName"] = commitment.startup.name
        item["entryType"] = "COMMITMENT"
        items.append(item)
    for funding_round in rounds:
        item = funding_round.to_dict()
        item["startupName"] = funding_round.startup.name
        item["entryType"] = "FUNDING_ROUND"
        items.append(item)
    return {"items": items}


@investors_bp.get("/interests")
@jwt_required()
@role_required("INVESTOR")
def list_interests():
    investor_id = int(get_jwt_identity())
    interests = (
        InvestorInterest.query.filter_by(investor_id=investor_id)
        .order_by(InvestorInterest.created_at.desc())
        .all()
    )
    items = []
    for interest in interests:
        item = interest.to_dict()
        item["startupName"] = interest.startup.name
        commitment = (
            InvestmentCommitment.query.filter_by(interest_id=interest.id, investor_id=investor_id)
            .order_by(InvestmentCommitment.created_at.desc())
            .first()
        )
        item["commitment"] = commitment.to_dict() if commitment else None
        items.append(item)
    return {"items": items}
