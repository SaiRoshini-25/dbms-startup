from app.extensions import db
from app.models import FundingRound, InvestmentCommitment, InvestorInterest, Milestone, Notification, Startup


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_create_and_update_funding_round(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()

    create_response = client.post(
        f"/api/startups/{startup.id}/funding-rounds",
        json={
            "roundName": "Seed Round",
            "roundType": "Seed",
            "amountRaised": 250000,
            "equityPercentage": 10,
            "announcedOn": "2026-03-01",
            "investmentRequirements": "Need compliance docs and growth metrics",
        },
        headers=auth_header(tokens["admin"]),
    )
    assert create_response.status_code == 201
    round_payload = create_response.get_json()["fundingRound"]
    round_id = round_payload["id"]
    assert round_payload["investmentRequirements"] == "Need compliance docs and growth metrics"
    assert round_payload["announcedOn"] == "2026-03-01"

    update_response = client.put(
        f"/api/startups/{startup.id}/funding-rounds/{round_id}",
        json={"roundStatus": "CLOSED", "mouStatus": "SIGNED", "closedOn": "2026-03-15"},
        headers=auth_header(tokens["admin"]),
    )
    assert update_response.status_code == 200
    updated_round = update_response.get_json()["fundingRound"]
    assert updated_round["roundStatus"] == "CLOSED"
    assert updated_round["closedOn"] == "2026-03-15"
    assert FundingRound.query.get(round_id).mou_status == "SIGNED"


def test_startup_rep_can_view_assigned_startup_details(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    db.session.add(Milestone(startup_id=startup.id, title="MVP", status="COMPLETED", progress_percent=100))
    db.session.commit()

    response = client.get("/api/startups/my", headers=auth_header(tokens["startup_rep"]))
    assert response.status_code == 200
    payload = response.get_json()["items"]
    assert len(payload) == 1
    assert payload[0]["milestones"][0]["title"] == "MVP"


def test_startup_rep_can_create_startup(client, tokens):
    response = client.post(
        "/api/startups",
        json={
            "name": "Nova Stack",
            "domain": "AI",
            "fundingStage": "Pre-Seed",
            "foundingDate": "2025-01-10",
            "teamSize": 3,
            "memberRole": "Co-Founder",
        },
        headers=auth_header(tokens["startup_rep"]),
    )
    assert response.status_code == 201
    payload = response.get_json()["startup"]
    assert payload["name"] == "Nova Stack"
    assert payload["members"][0]["memberRole"] == "Co-Founder"


def test_search_returns_matching_entities(client, tokens):
    response = client.get("/api/startups/search?q=Alpha", headers=auth_header(tokens["admin"]))
    assert response.status_code == 200
    data = response.get_json()
    assert data["startups"][0]["name"] == "Alpha Labs"


def test_investor_portfolio_returns_created_round(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    response = client.post(
        f"/api/startups/{startup.id}/funding-rounds",
        json={
            "roundName": "Bridge",
            "roundType": "Seed",
            "amountRaised": 150000,
            "equityPercentage": 5,
            "leadInvestorId": 2,
        },
        headers=auth_header(tokens["admin"]),
    )
    assert response.status_code == 201

    portfolio_response = client.get("/api/investors/portfolio", headers=auth_header(tokens["investor"]))
    assert portfolio_response.status_code == 200
    items = portfolio_response.get_json()["items"]
    assert any(item["startupName"] == "Alpha Labs" and item["entryType"] == "FUNDING_ROUND" for item in items)


def test_startup_rep_can_accept_investor_interest(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))
    interest_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 125000, "equityPercentage": 6, "investorNotes": "Interested in traction"},
        headers=auth_header(tokens["investor"]),
    )
    assert interest_response.status_code == 201
    interest_id = interest_response.get_json()["interest"]["id"]

    accept_response = client.put(
        f"/api/investors/interest/{interest_id}/accept",
        json={"responseNotes": "Accepted"},
        headers=auth_header(tokens["startup_rep"]),
    )
    assert accept_response.status_code == 200
    payload = accept_response.get_json()
    assert payload["interest"]["status"] == "ACCEPTED"
    assert payload["commitment"]["status"] == "APPROVED"


def test_investor_interests_returns_interest_entries(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))

    interest_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 125000, "equityPercentage": 6, "investorNotes": "Interested in traction"},
        headers=auth_header(tokens["investor"]),
    )
    assert interest_response.status_code == 201

    interests_response = client.get("/api/investors/interests", headers=auth_header(tokens["investor"]))
    assert interests_response.status_code == 200
    items = interests_response.get_json()["items"]
    assert any(
        item["startupName"] == "Alpha Labs"
        and item["status"] == "INITIATED"
        and item["commitment"]["requestedAmount"] == 125000
        for item in items
    )


def test_startup_rep_can_publish_startup(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()

    response = client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))

    assert response.status_code == 200
    payload = response.get_json()["startup"]
    assert payload["isPublished"] is True
    assert payload["incubatorStatus"] == "PUBLISHED"


def test_investor_commitment_approval_updates_startup_totals(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))

    interest_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 300000, "equityPercentage": 12, "investorNotes": "Interested in growth"},
        headers=auth_header(tokens["investor"]),
    )
    assert interest_response.status_code == 201
    interest_id = interest_response.get_json()["interest"]["id"]
    commitment_id = interest_response.get_json()["commitment"]["id"]

    approval_response = client.put(
        f"/api/investors/interest/{interest_id}/accept",
        json={"responseNotes": "Approved after review"},
        headers=auth_header(tokens["startup_rep"]),
    )
    assert approval_response.status_code == 200
    startup_payload = Startup.query.get(startup.id).to_dict()
    assert startup_payload["totalRaised"] == 300000
    assert startup_payload["equityAllocated"] == 12
    assert startup_payload["investorCount"] == 1
    assert InvestmentCommitment.query.get(commitment_id).status == "APPROVED"
    generated_round = FundingRound.query.filter_by(startup_id=startup.id, lead_investor_id=2, round_name=f"Commitment {commitment_id}").first()
    assert generated_round is not None
    assert generated_round.amount_raised == 300000
    assert generated_round.round_status == "CLOSED"

    portfolio_response = client.get("/api/investors/portfolio", headers=auth_header(tokens["investor"]))
    assert portfolio_response.status_code == 200
    portfolio_items = portfolio_response.get_json()["items"]
    assert any(item["entryType"] == "COMMITMENT" and item["status"] == "APPROVED" for item in portfolio_items)


def test_startup_rep_can_reject_commitment(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))

    interest_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 100000, "equityPercentage": 4},
        headers=auth_header(tokens["investor"]),
    )
    assert interest_response.status_code == 201
    interest_id = interest_response.get_json()["interest"]["id"]
    commitment_id = interest_response.get_json()["commitment"]["id"]

    reject_response = client.put(
        f"/api/investors/interest/{interest_id}/reject",
        json={"responseNotes": "Terms do not fit"},
        headers=auth_header(tokens["startup_rep"]),
    )
    assert reject_response.status_code == 200
    assert reject_response.get_json()["commitment"]["status"] == "REJECTED"
    assert Startup.query.get(startup.id).to_dict()["totalRaised"] == 0
    assert FundingRound.query.filter_by(startup_id=startup.id, lead_investor_id=2, round_name=f"Commitment {commitment_id}").first() is None


def test_marking_notification_read_deletes_it(client, tokens):
    db.session.add(
        Notification(
            recipient_user_id=2,
            title="Interest update",
            message="A startup responded to your interest.",
        )
    )
    db.session.commit()
    notification_id = Notification.query.filter_by(recipient_user_id=2).first().id

    response = client.put(f"/api/notifications/{notification_id}/read", headers=auth_header(tokens["investor"]))

    assert response.status_code == 200
    assert response.get_json()["notificationId"] == notification_id
    assert Notification.query.get(notification_id) is None


def test_funding_round_closed_status_requires_closed_on(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()

    response = client.post(
        f"/api/startups/{startup.id}/funding-rounds",
        json={
            "roundName": "Series A",
            "roundType": "Series A",
            "amountRaised": 500000,
            "equityPercentage": 15,
            "roundStatus": "CLOSED",
        },
        headers=auth_header(tokens["admin"]),
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "closedOn is required when roundStatus is CLOSED"


def test_accepted_interest_creates_notifications_and_keeps_startup_open_for_more_offers(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))

    interest_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 200000, "equityPercentage": 8},
        headers=auth_header(tokens["investor"]),
    )
    assert interest_response.status_code == 201
    interest_id = interest_response.get_json()["interest"]["id"]

    startup_notifications = Notification.query.filter_by(recipient_user_id=3).all()
    assert any(notification.title == "New Investor Interest" for notification in startup_notifications)

    accept_response = client.put(
        f"/api/investors/interest/{interest_id}/accept",
        json={"responseNotes": "Accepted"},
        headers=auth_header(tokens["startup_rep"]),
    )
    assert accept_response.status_code == 200

    investor_notifications = Notification.query.filter_by(recipient_user_id=2).all()
    assert any(notification.title == "Interest Accepted" for notification in investor_notifications)

    investor_list_response = client.get("/api/startups", headers=auth_header(tokens["investor"]))
    assert investor_list_response.status_code == 200
    assert any(item["name"] == "Alpha Labs" and item["acceptingInvestment"] is True for item in investor_list_response.get_json()["items"])

    second_interest_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 50000, "equityPercentage": 2},
        headers=auth_header(tokens["investor"]),
    )
    assert second_interest_response.status_code == 201
    assert InvestorInterest.query.filter_by(startup_id=startup.id, investor_id=2).count() == 2


def test_investor_can_submit_multiple_offers_without_waiting(client, tokens):
    startup = Startup.query.filter_by(name="Alpha Labs").first()
    client.put(f"/api/startups/{startup.id}/publish", headers=auth_header(tokens["startup_rep"]))

    first_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 100000, "equityPercentage": 4},
        headers=auth_header(tokens["investor"]),
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/investors/interest",
        json={"startupId": startup.id, "requestedAmount": 150000, "equityPercentage": 5},
        headers=auth_header(tokens["investor"]),
    )
    assert second_response.status_code == 201

    assert InvestorInterest.query.filter_by(startup_id=startup.id, investor_id=2).count() == 2
    assert InvestmentCommitment.query.filter_by(startup_id=startup.id, investor_id=2).count() == 2
