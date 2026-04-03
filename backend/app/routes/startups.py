from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from ..extensions import db
from ..models import FundingRound, InvestmentCommitment, Milestone, Startup, StartupMember, User
from ..utils import (
    create_notification,
    error_response,
    get_current_role,
    get_startup_ids_for_user,
    log_activity,
    parse_date,
    recalculate_startup_totals,
    refresh_startup_visibility,
    role_required,
    startup_accepting_investment,
    user_owns_startup,
)

startups_bp = Blueprint("startups", __name__)


VALID_MOU_STATUSES = {"PENDING", "SIGNED", "CANCELLED"}
VALID_ROUND_STATUSES = {"OPEN", "IN_PROGRESS", "CLOSED"}


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
        log_activity(actor_user_id, "funding_round", funding_round.id, "CREATE", f"Created funding round {funding_round.round_name} from commitment")
        return funding_round

    funding_round.round_type = commitment.startup.funding_stage or funding_round.round_type
    funding_round.amount_raised = commitment.approved_amount or commitment.requested_amount
    funding_round.equity_percentage = commitment.equity_percentage
    funding_round.mou_status = "SIGNED"
    funding_round.round_status = "CLOSED"
    funding_round.announced_on = funding_round.announced_on or round_date
    funding_round.closed_on = round_date
    funding_round.investment_requirements = commitment.startup_requirements
    log_activity(actor_user_id, "funding_round", funding_round.id, "UPDATE", f"Updated funding round {funding_round.round_name} from commitment")
    return funding_round


def _remove_commitment_funding_round(commitment, actor_user_id):
    funding_round = _get_commitment_funding_round(commitment)
    if funding_round is None:
        return
    log_activity(actor_user_id, "funding_round", funding_round.id, "DELETE", f"Removed funding round {funding_round.round_name} after commitment rejection")
    db.session.delete(funding_round)


def _validate_funding_round_payload(startup, data, existing_round=None):
    try:
        amount_raised = float(data.get("amountRaised", existing_round.amount_raised if existing_round else 0))
        equity_percentage = float(data.get("equityPercentage", existing_round.equity_percentage if existing_round else 0))
    except (TypeError, ValueError):
        return None, error_response("amountRaised and equityPercentage must be valid numbers", 400)

    if amount_raised < 0:
        return None, error_response("amountRaised must be greater than or equal to 0", 400)
    if equity_percentage < 0 or equity_percentage > 100:
        return None, error_response("equityPercentage must be between 0 and 100", 400)

    mou_status = (data.get("mouStatus", existing_round.mou_status if existing_round else "PENDING") or "PENDING").upper()
    if mou_status not in VALID_MOU_STATUSES:
        return None, error_response("mouStatus must be one of PENDING, SIGNED, CANCELLED", 400)

    round_status = (data.get("roundStatus", existing_round.round_status if existing_round else "OPEN") or "OPEN").upper()
    if round_status not in VALID_ROUND_STATUSES:
        return None, error_response("roundStatus must be one of OPEN, IN_PROGRESS, CLOSED", 400)

    lead_investor_id = data.get("leadInvestorId", existing_round.lead_investor_id if existing_round else None)
    if lead_investor_id in ("", 0):
        lead_investor_id = None
    if lead_investor_id is not None:
        try:
            lead_investor_id = int(lead_investor_id)
        except (TypeError, ValueError):
            return None, error_response("leadInvestorId must be a valid investor id", 400)
        investor = User.query.get_or_404(lead_investor_id)
        if investor.role.name != "INVESTOR":
            return None, error_response("leadInvestorId must belong to an investor", 400)

    round_name = (data.get("roundName", existing_round.round_name if existing_round else "") or "").strip()
    round_type = (data.get("roundType", existing_round.round_type if existing_round else "") or "").strip()
    if not round_name or not round_type:
        return None, error_response("roundName and roundType are required", 400)

    announced_on = parse_date(data.get("announcedOn")) if data.get("announcedOn") else (existing_round.announced_on if existing_round else None)
    closed_on = parse_date(data.get("closedOn")) if data.get("closedOn") else (existing_round.closed_on if existing_round else None)

    if round_status == "CLOSED" and not closed_on:
        return None, error_response("closedOn is required when roundStatus is CLOSED", 400)
    if closed_on and announced_on and closed_on < announced_on:
        return None, error_response("closedOn cannot be earlier than announcedOn", 400)

    duplicate_query = FundingRound.query.filter_by(
        startup_id=startup.id,
        round_name=round_name,
        lead_investor_id=lead_investor_id,
    )
    if existing_round is not None:
        duplicate_query = duplicate_query.filter(FundingRound.id != existing_round.id)
    if duplicate_query.first():
        return None, error_response("Duplicate funding round for this startup and investor", 409)

    other_equity = sum(round_item.equity_percentage for round_item in startup.funding_rounds if existing_round is None or round_item.id != existing_round.id)
    if other_equity + equity_percentage > 100:
        return None, error_response("Total equity percentage cannot exceed 100", 400)

    return {
        "round_name": round_name,
        "round_type": round_type,
        "amount_raised": amount_raised,
        "equity_percentage": equity_percentage,
        "mou_status": mou_status,
        "round_status": round_status,
        "lead_investor_id": lead_investor_id,
        "announced_on": announced_on,
        "closed_on": closed_on,
        "investment_requirements": data.get("investmentRequirements", existing_round.investment_requirements if existing_round else None),
    }, None


@startups_bp.get("")
@jwt_required()
def list_startups():
    query = Startup.query

    domain = request.args.get("domain")
    funding_stage = request.args.get("fundingStage")
    min_score = request.args.get("minScore", type=float)
    search_query = request.args.get("q")

    if domain:
        query = query.filter(Startup.domain.ilike(f"%{domain}%"))
    if funding_stage:
        query = query.filter_by(funding_stage=funding_stage)
    if min_score is not None:
        query = query.filter(Startup.performance_score >= min_score)
    if search_query:
        query = query.filter(
            or_(
                Startup.name.ilike(f"%{search_query}%"),
                Startup.domain.ilike(f"%{search_query}%"),
                Startup.description.ilike(f"%{search_query}%"),
            )
        )
    startups = query.order_by(Startup.created_at.desc()).all()
    if get_current_role() == "INVESTOR":
        startups = [startup for startup in startups if startup_accepting_investment(startup)]
    return {"items": [startup.to_dict() for startup in startups]}


@startups_bp.post("")
@jwt_required()
@role_required("ADMIN", "STARTUP_REP")
def create_startup():
    data = request.get_json() or {}
    required_fields = ["name", "domain", "fundingStage", "foundingDate", "teamSize"]
    missing = [field for field in required_fields if data.get(field) in (None, "")]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)
    if Startup.query.filter_by(name=data["name"]).first():
        return error_response("Startup with this name already exists", 409)
    creator_id = int(get_jwt_identity())

    startup = Startup(
        name=data["name"],
        domain=data["domain"],
        funding_stage=data["fundingStage"],
        founding_date=parse_date(data["foundingDate"]),
        team_size=data["teamSize"],
        headquarters_city=data.get("headquartersCity"),
        website_url=data.get("websiteUrl"),
        description=data.get("description"),
        incubator_status=data.get("incubatorStatus", "ACTIVE"),
        funding_status=data.get("fundingStatus", "BOOTSTRAPPED"),
        funding_requirements=data.get("fundingRequirements"),
        performance_score=data.get("performanceScore"),
        target_amount=float(data.get("targetAmount", 0) or 0),
        created_by=creator_id,
    )
    db.session.add(startup)
    db.session.flush()

    if get_current_role() == "STARTUP_REP":
        db.session.add(
            StartupMember(
                startup_id=startup.id,
                user_id=creator_id,
                member_role=data.get("memberRole", "Founder"),
                is_primary_contact=True,
            )
        )

    for milestone_data in data.get("milestones", []):
        db.session.add(
            Milestone(
                startup_id=startup.id,
                title=milestone_data["title"],
                description=milestone_data.get("description"),
                target_date=parse_date(milestone_data.get("targetDate")),
                status=milestone_data.get("status", "PENDING"),
                progress_percent=milestone_data.get("progressPercent", 0),
            )
        )

    log_activity(creator_id, "startup", startup.id, "CREATE", f"Created startup {startup.name}")
    db.session.commit()
    return {"message": "Startup created", "startup": startup.to_dict()}, 201


@startups_bp.put("/<int:startup_id>/publish")
@jwt_required()
@role_required("ADMIN", "STARTUP_REP")
def publish_startup(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    user_id = int(get_jwt_identity())
    current_role = get_current_role()
    if current_role == "STARTUP_REP" and not user_owns_startup(user_id, startup_id):
        return error_response("Forbidden", 403)

    startup.is_published = True
    startup.published_at = datetime.utcnow()
    startup.incubator_status = "PUBLISHED"

    admin_user_ids = [user.id for user in User.query.join(User.role).filter_by(name="ADMIN").all()]
    for recipient_user_id in admin_user_ids:
        create_notification(
            recipient_user_id,
            "Startup Published",
            f"{startup.name} is now open for investor review.",
            link="/startups",
        )

    log_activity(user_id, "startup", startup.id, "UPDATE", f"Published startup {startup.name}")
    db.session.commit()
    return {"message": "Startup published", "startup": startup.to_dict()}


@startups_bp.put("/<int:startup_id>")
@jwt_required()
@role_required("ADMIN", "STARTUP_REP")
def update_startup(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    data = request.get_json() or {}
    old_name = startup.name
    user_id = int(get_jwt_identity())
    current_role = get_current_role()

    if current_role == "STARTUP_REP" and not user_owns_startup(user_id, startup_id):
        return error_response("Forbidden", 403)

    startup.name = data.get("name", startup.name)
    startup.domain = data.get("domain", startup.domain)
    startup.funding_stage = data.get("fundingStage", startup.funding_stage)
    startup.team_size = data.get("teamSize", startup.team_size)
    startup.headquarters_city = data.get("headquartersCity", startup.headquarters_city)
    startup.website_url = data.get("websiteUrl", startup.website_url)
    startup.description = data.get("description", startup.description)
    if current_role == "ADMIN":
        startup.incubator_status = data.get("incubatorStatus", startup.incubator_status)
    startup.funding_status = data.get("fundingStatus", startup.funding_status)
    startup.funding_requirements = data.get("fundingRequirements", startup.funding_requirements)
    startup.performance_score = data.get("performanceScore", startup.performance_score)
    if data.get("targetAmount") is not None:
        startup.target_amount = float(data.get("targetAmount") or 0)
    if data.get("foundingDate"):
        startup.founding_date = parse_date(data["foundingDate"])

    log_activity(
        user_id,
        "startup",
        startup.id,
        "UPDATE",
        f"Updated startup {old_name}",
        old_values=old_name,
        new_values=startup.name,
    )
    db.session.commit()
    return {"message": "Startup updated", "startup": startup.to_dict()}


@startups_bp.delete("/<int:startup_id>")
@jwt_required()
@role_required("ADMIN")
def delete_startup(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    name = startup.name
    db.session.delete(startup)
    log_activity(int(get_jwt_identity()), "startup", startup_id, "DELETE", f"Removed startup {name}")
    db.session.commit()
    return {"message": "Startup removed"}


@startups_bp.get("/my")
@jwt_required()
@role_required("STARTUP_REP")
def my_startups():
    user_id = int(get_jwt_identity())
    startup_ids = get_startup_ids_for_user(user_id)
    startups = Startup.query.filter(Startup.id.in_(startup_ids)).order_by(Startup.created_at.desc()).all() if startup_ids else []
    return {"items": [startup.to_dict() for startup in startups]}


@startups_bp.post("/<int:startup_id>/milestones")
@jwt_required()
@role_required("ADMIN", "STARTUP_REP")
def create_milestone(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    user_id = int(get_jwt_identity())
    if get_current_role() == "STARTUP_REP" and not user_owns_startup(user_id, startup_id):
        return error_response("Forbidden", 403)

    data = request.get_json() or {}
    if not data.get("title"):
        return error_response("title is required", 400)

    milestone = Milestone(
        startup_id=startup.id,
        title=data["title"],
        description=data.get("description"),
        target_date=parse_date(data.get("targetDate")),
        completion_date=parse_date(data.get("completionDate")),
        status=data.get("status", "PENDING"),
        progress_percent=float(data.get("progressPercent", 0)),
    )
    db.session.add(milestone)
    db.session.flush()
    log_activity(user_id, "milestone", milestone.id, "CREATE", f"Created milestone {milestone.title}")
    db.session.commit()
    return {"message": "Milestone created", "milestone": milestone.to_dict()}, 201


@startups_bp.put("/<int:startup_id>/milestones/<int:milestone_id>")
@jwt_required()
@role_required("ADMIN", "STARTUP_REP")
def update_milestone(startup_id, milestone_id):
    milestone = Milestone.query.filter_by(id=milestone_id, startup_id=startup_id).first_or_404()
    user_id = int(get_jwt_identity())
    if get_current_role() == "STARTUP_REP" and not user_owns_startup(user_id, startup_id):
        return error_response("Forbidden", 403)

    data = request.get_json() or {}
    milestone.title = data.get("title", milestone.title)
    milestone.description = data.get("description", milestone.description)
    if data.get("targetDate"):
        milestone.target_date = parse_date(data["targetDate"])
    if data.get("completionDate"):
        milestone.completion_date = parse_date(data["completionDate"])
    milestone.status = data.get("status", milestone.status)
    milestone.progress_percent = float(data.get("progressPercent", milestone.progress_percent))

    log_activity(user_id, "milestone", milestone.id, "UPDATE", f"Updated milestone {milestone.title}")
    db.session.commit()
    return {"message": "Milestone updated", "milestone": milestone.to_dict()}


@startups_bp.post("/<int:startup_id>/funding-rounds")
@jwt_required()
@role_required("ADMIN")
def create_funding_round(startup_id):
    startup = Startup.query.get_or_404(startup_id)
    data = request.get_json() or {}
    required_fields = ["roundName", "roundType", "amountRaised", "equityPercentage"]
    missing = [field for field in required_fields if data.get(field) in (None, "")]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    funding_round_values, validation_error = _validate_funding_round_payload(startup, data)
    if validation_error:
        return validation_error

    funding_round = FundingRound(
        startup_id=startup_id,
        created_by=int(get_jwt_identity()),
        **funding_round_values,
    )
    db.session.add(funding_round)
    db.session.flush()
    log_activity(int(get_jwt_identity()), "funding_round", funding_round.id, "CREATE", f"Created funding round {funding_round.round_name}")
    db.session.commit()
    return {"message": "Funding round created", "fundingRound": funding_round.to_dict()}, 201


@startups_bp.put("/<int:startup_id>/funding-rounds/<int:funding_round_id>")
@jwt_required()
@role_required("ADMIN")
def update_funding_round(startup_id, funding_round_id):
    funding_round = FundingRound.query.filter_by(id=funding_round_id, startup_id=startup_id).first_or_404()
    startup = Startup.query.get_or_404(startup_id)
    data = request.get_json() or {}

    funding_round_values, validation_error = _validate_funding_round_payload(startup, data, existing_round=funding_round)
    if validation_error:
        return validation_error

    for field_name, field_value in funding_round_values.items():
        setattr(funding_round, field_name, field_value)

    refresh_startup_visibility(startup)
    log_activity(int(get_jwt_identity()), "funding_round", funding_round.id, "UPDATE", f"Updated funding round {funding_round.round_name}")
    db.session.commit()
    return {"message": "Funding round updated", "fundingRound": funding_round.to_dict()}


@startups_bp.put("/commitments/<int:commitment_id>/decision")
@jwt_required()
@role_required("ADMIN", "STARTUP_REP")
def decide_commitment(commitment_id):
    commitment = InvestmentCommitment.query.get_or_404(commitment_id)
    user_id = int(get_jwt_identity())
    current_role = get_current_role()
    if current_role == "STARTUP_REP" and not user_owns_startup(user_id, commitment.startup_id):
        return error_response("Forbidden", 403)

    data = request.get_json() or {}
    decision = (data.get("decision") or "").upper()
    if decision not in {"APPROVED", "REJECTED"}:
        return error_response("decision must be APPROVED or REJECTED", 400)

    if decision == "APPROVED":
        approved_amount = float(data.get("approvedAmount", commitment.requested_amount))
        if commitment.startup.equity_allocated + commitment.equity_percentage > 100:
            approved_other = sum(
                item.equity_percentage for item in commitment.startup.commitments if item.id != commitment.id and item.status == "APPROVED"
            )
            if approved_other + commitment.equity_percentage > 100:
                return error_response("Total equity percentage cannot exceed 100", 400)
        commitment.status = "APPROVED"
        commitment.approved_amount = approved_amount
        commitment.agreed_at = datetime.utcnow()
        commitment.startup.funding_status = "IN_PROGRESS"
        _sync_commitment_funding_round(commitment, user_id)
        if commitment.interest:
            commitment.interest.status = "ACCEPTED"
            commitment.interest.pipeline_stage = "COMMITMENT_APPROVED"
            commitment.interest.response_notes = data.get("decisionNotes")
            commitment.interest.responded_by = user_id
    else:
        commitment.status = "REJECTED"
        commitment.approved_amount = 0
        _remove_commitment_funding_round(commitment, user_id)
        if commitment.interest:
            commitment.interest.status = "REJECTED"
            commitment.interest.pipeline_stage = "COMMITMENT_REJECTED"
            commitment.interest.response_notes = data.get("decisionNotes")
            commitment.interest.responded_by = user_id

    commitment.decision_notes = data.get("decisionNotes")
    commitment.decided_by = user_id
    recalculate_startup_totals(commitment.startup)
    create_notification(
        commitment.investor_id,
        "Investment Commitment Updated",
        f"{commitment.startup.name} marked your commitment as {commitment.status}.",
        link="/portfolio",
    )
    log_activity(user_id, "investment_commitment", commitment.id, "UPDATE", f"{commitment.status.title()} investment commitment")
    db.session.commit()
    return {"message": "Commitment updated", "commitment": commitment.to_dict(), "startup": commitment.startup.to_dict()}


@startups_bp.get("/search")
@jwt_required()
def search_entities():
    query_text = request.args.get("q", "").strip()
    if not query_text:
        return error_response("q is required", 400)

    startups = (
        Startup.query.filter(
            or_(
                Startup.name.ilike(f"%{query_text}%"),
                Startup.domain.ilike(f"%{query_text}%"),
                Startup.description.ilike(f"%{query_text}%"),
            )
        )
        .order_by(Startup.name.asc())
        .limit(10)
        .all()
    )
    users = (
        User.query.join(User.role)
        .filter(
            or_(
                User.full_name.ilike(f"%{query_text}%"),
                User.email.ilike(f"%{query_text}%"),
                User.organization_name.ilike(f"%{query_text}%"),
            )
        )
        .order_by(User.full_name.asc())
        .limit(10)
        .all()
    )

    return {
        "startups": [{"id": startup.id, "name": startup.name, "domain": startup.domain} for startup in startups],
        "users": [{"id": user.id, "fullName": user.full_name, "email": user.email, "role": user.role.name} for user in users],
        "viewerRole": get_current_role(),
    }
