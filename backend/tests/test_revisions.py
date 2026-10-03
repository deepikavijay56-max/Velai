import pytest
import httpx


@pytest.mark.asyncio
async def test_revision_limits_and_completion(poster_client: httpx.AsyncClient, doer_client: httpx.AsyncClient):
    """Deliverable submission, revision limit enforcement, approval, and record-only payments."""
    # 1. Poster creates gig with strictly 1 revision
    g_res = await poster_client.post("/api/v1/gigs", json={
        "title": "Edit Department Promo Video",
        "category": "Video & Audio",
        "description": "Short promo video for department open day with background music and subtitles.",
        "deliverables": ["1080p MP4 file"],
        "budget_min": 1000,
        "budget_max": 2000,
        "deadline": "2026-11-25T18:00:00Z",
        "revisions": 1,
        "skills": ["Premiere Pro", "Video Editing"]
    })
    assert g_res.status_code == 200
    gig_id = g_res.json()["id"]

    # 2. Doer applies & Poster accepts
    app_res = await doer_client.post(f"/api/v1/gigs/{gig_id}/apply", json={
        "pitch": "I edit videos for student events.",
        "proposed_price": 1500,
        "proposed_days": 2
    })
    app_id = app_res.json()["id"]

    contract_res = await poster_client.post(f"/api/v1/applications/{app_id}/accept")
    contract_id = contract_res.json()["id"]

    # Doer confirms -> InProgress
    await doer_client.post(f"/api/v1/contracts/{contract_id}/confirm")

    # 3. Doer submits Deliverable v1 -> Gig becomes Delivered
    deliv1_res = await doer_client.post(f"/api/v1/contracts/{contract_id}/deliver", json={
        "file_url": "https://storage.velai/v1.mp4",
        "note": "Here is version 1 of the promo video."
    })
    assert deliv1_res.status_code == 200
    assert deliv1_res.json()["version"] == 1
    deliv1_id = deliv1_res.json()["id"]

    gig_check = await poster_client.get(f"/api/v1/gigs/{gig_id}")
    assert gig_check.json()["status"] == "Delivered"

    # 4. Poster requests Revision 1 of 1 -> Gig returns to InProgress
    rev1_res = await poster_client.post(f"/api/v1/deliverables/{deliv1_id}/revise", json={
        "revision_reason": "Please lower the background music volume during interviews."
    })
    assert rev1_res.status_code == 200
    assert rev1_res.json()["status"] == "revision_requested"

    gig_check = await poster_client.get(f"/api/v1/gigs/{gig_id}")
    assert gig_check.json()["status"] == "InProgress"

    # 5. Doer submits Deliverable v2 -> Gig becomes Delivered
    deliv2_res = await doer_client.post(f"/api/v1/contracts/{contract_id}/deliver", json={
        "file_url": "https://storage.velai/v2.mp4",
        "note": "Adjusted audio balance as requested."
    })
    assert deliv2_res.status_code == 200
    assert deliv2_res.json()["version"] == 2
    deliv2_id = deliv2_res.json()["id"]

    # 6. Poster attempts Revision 2 (when agreed limit is 1) -> STRICTLY REJECTED with 400!
    rev2_res = await poster_client.post(f"/api/v1/deliverables/{deliv2_id}/revise", json={
        "revision_reason": "Can you change the ending logo animation too?"
    })
    assert rev2_res.status_code == 400
    assert "Revision limit reached (1/1)" in rev2_res.json()["detail"]

    # 7. Poster approves Deliverable v2 -> Gig becomes Completed
    approve_res = await poster_client.post(f"/api/v1/deliverables/{deliv2_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "accepted"

    gig_check = await poster_client.get(f"/api/v1/gigs/{gig_id}")
    assert gig_check.json()["status"] == "Completed"

    # 8. Record-only UPI payment confirmation
    pay_paid = await poster_client.post(f"/api/v1/contracts/{contract_id}/payment/paid")
    assert pay_paid.status_code == 200
    assert pay_paid.json()["poster_marked_paid"] is True

    pay_rcvd = await doer_client.post(f"/api/v1/contracts/{contract_id}/payment/received")
    assert pay_rcvd.status_code == 200
    assert pay_rcvd.json()["status"] == "completed"

    # 9. Two-way reviews
    r1 = await poster_client.post(f"/api/v1/contracts/{contract_id}/review", json={
        "rating": 5, "comment": "Great video editor!", "tags": ["creative"]
    })
    assert r1.status_code == 200

    r2 = await doer_client.post(f"/api/v1/contracts/{contract_id}/review", json={
        "rating": 5, "comment": "Prompt feedback and clear instructions.", "tags": ["clear brief"]
    })
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_academic_dishonesty_keyword_filter(poster_client: httpx.AsyncClient):
    """Academic dishonesty keywords are automatically flagged and excluded from browse feed."""
    res = await poster_client.post("/api/v1/gigs", json={
        "title": "Need someone to do my physics exam and write my assignment",
        "category": "Writing",
        "description": "Will pay to have my homework solved and exam questions answered.",
        "deliverables": ["Answers"],
        "budget_min": 1000,
        "budget_max": 2000,
        "deadline": "2026-11-25T18:00:00Z",
        "revisions": 1,
        "skills": []
    })
    assert res.status_code == 200
    assert res.json()["is_flagged_academic"] is True
    assert "exam" in res.json()["flag_reason"]

    # Must NOT show up in public browse feed
    feed_res = await poster_client.get("/api/v1/gigs")
    assert feed_res.status_code == 200
    for gig in feed_res.json():
        assert not gig["is_flagged_academic"]
