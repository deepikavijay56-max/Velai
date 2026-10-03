from datetime import datetime, timedelta, timezone

import httpx
import pytest


async def login(client: httpx.AsyncClient, email: str, name: str) -> dict[str, str]:
    otp_response = await client.post("/api/v1/auth/request-otp", json={"email": email})
    assert otp_response.status_code == 200
    otp_code = otp_response.json()["dev_mock_otp"]
    assert otp_code

    auth_response = await client.post(
        "/api/v1/auth/verify-otp",
        json={"email": email, "otp_code": otp_code, "name": name},
    )
    assert auth_response.status_code == 200
    return {"Authorization": f"Bearer {auth_response.json()['access_token']}"}


@pytest.mark.asyncio
async def test_phase_one_gig_workflow(client: httpx.AsyncClient):
    poster_headers = await login(client, "poster@psgtech.ac.in", "Gig Poster")
    doer_headers = await login(client, "doer@psgtech.ac.in", "Gig Doer")

    gig_response = await client.post(
        "/api/v1/gigs",
        headers=poster_headers,
        json={
            "title": "Design an event poster",
            "category": "Design",
            "description": "Create a polished poster for a campus event.",
            "deliverables": ["Final poster file"],
            "budget_min": 500,
            "budget_max": 1000,
            "deadline": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "revisions": 1,
        },
    )
    assert gig_response.status_code == 200, gig_response.text
    gig = gig_response.json()

    application_response = await client.post(
        f"/api/v1/gigs/{gig['id']}/apply",
        headers=doer_headers,
        json={
            "pitch": "I can design this event poster with a clear visual hierarchy.",
            "proposed_price": 800,
            "proposed_days": 4,
        },
    )
    assert application_response.status_code == 200, application_response.text

    contract_response = await client.post(
        f"/api/v1/applications/{application_response.json()['id']}/accept",
        headers=poster_headers,
    )
    assert contract_response.status_code == 200, contract_response.text
    contract = contract_response.json()
    assert contract["status"] == "pending_confirmation"

    mine_response = await client.get("/api/v1/contracts/mine", headers=doer_headers)
    assert mine_response.status_code == 200, mine_response.text
    assert mine_response.json()[0]["gig"]["id"] == gig["id"]

    by_gig_response = await client.get(
        f"/api/v1/contracts/by-gig/{gig['id']}",
        headers=doer_headers,
    )
    assert by_gig_response.status_code == 200, by_gig_response.text

    confirmation_response = await client.post(
        f"/api/v1/contracts/{contract['id']}/confirm",
        headers=doer_headers,
    )
    assert confirmation_response.status_code == 200, confirmation_response.text
    assert confirmation_response.json()["status"] == "active"

    sent_message = await client.post(
        f"/api/v1/gigs/{gig['id']}/messages",
        headers=doer_headers,
        json={"body": "I have started on the poster."},
    )
    assert sent_message.status_code == 200, sent_message.text
    messages_response = await client.get(
        f"/api/v1/gigs/{gig['id']}/messages",
        headers=poster_headers,
    )
    assert messages_response.status_code == 200, messages_response.text
    assert messages_response.json()[0]["body"] == "I have started on the poster."

    delivery_response = await client.post(
        f"/api/v1/contracts/{contract['id']}/deliver",
        headers=doer_headers,
        json={"file_url": "https://example.test/event-poster.png", "note": "Final version"},
    )
    assert delivery_response.status_code == 200, delivery_response.text

    approval_response = await client.post(
        f"/api/v1/deliverables/{delivery_response.json()['id']}/approve",
        headers=poster_headers,
    )
    assert approval_response.status_code == 200, approval_response.text

    review_response = await client.post(
        f"/api/v1/contracts/{contract['id']}/review",
        headers=poster_headers,
        json={"rating": 5, "comment": "Clear communication and great work."},
    )
    assert review_response.status_code == 200, review_response.text
    assert review_response.json()["rating"] == 5
