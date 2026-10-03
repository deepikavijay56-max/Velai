import pytest
import httpx


@pytest.mark.asyncio
async def test_apply_and_accept_flow(poster_client: httpx.AsyncClient, doer_client: httpx.AsyncClient):
    """Full application, acceptance, and double confirmation flow."""
    # 1. Poster creates a gig
    g_res = await poster_client.post("/api/v1/gigs", json={
        "title": "Create Figma Mockup for College Event",
        "category": "Design",
        "description": "Design an interactive prototype for our college fest schedule.",
        "deliverables": ["Figma source file", "Clickable prototype link"],
        "budget_min": 1500,
        "budget_max": 2500,
        "deadline": "2026-11-20T18:00:00Z",
        "revisions": 2,
        "skills": ["Figma", "UI/UX Design"]
    })
    assert g_res.status_code == 200
    gig = g_res.json()
    gig_id = gig["id"]

    # 2. Doer applies to the gig
    app_res = await doer_client.post(f"/api/v1/gigs/{gig_id}/apply", json={
        "pitch": "Experienced UI/UX designer with 5+ college projects. Can deliver in 3 days.",
        "sample_url": "https://figma.com/@pooja",
        "proposed_price": 2000,
        "proposed_days": 3
    })
    assert app_res.status_code == 200
    application = app_res.json()
    assert application["status"] == "pending"
    assert application["proposed_price"] == 2000
    app_id = application["id"]

    # 3. Prevent duplicate application
    dup_res = await doer_client.post(f"/api/v1/gigs/{gig_id}/apply", json={
        "pitch": "Another pitch from the same student.",
        "proposed_price": 2000,
        "proposed_days": 3
    })
    assert dup_res.status_code == 400
    assert "already applied" in dup_res.json()["detail"]

    # 4. Prevent poster from applying to own gig
    self_res = await poster_client.post(f"/api/v1/gigs/{gig_id}/apply", json={
        "pitch": "Trying to apply to my own gig.",
        "proposed_price": 2000,
        "proposed_days": 3
    })
    assert self_res.status_code == 400
    assert "cannot apply to your own gig" in self_res.json()["detail"]

    # 5. Poster views applicants
    apps_list = await poster_client.get(f"/api/v1/gigs/{gig_id}/applications")
    assert apps_list.status_code == 200
    assert len(apps_list.json()) == 1

    # 6. Poster accepts applicant -> creates Draft Contract
    accept_res = await poster_client.post(f"/api/v1/applications/{app_id}/accept")
    assert accept_res.status_code == 200
    contract = accept_res.json()
    assert contract["status"] == "pending_confirmation"
    assert contract["agreed_price"] == 2000
    assert contract["confirmed_by_poster_at"] is not None
    assert contract["confirmed_by_doer_at"] is None
    contract_id = contract["id"]

    # 7. Doer confirms agreement -> transitions Gig to InProgress
    confirm_res = await doer_client.post(f"/api/v1/contracts/{contract_id}/confirm")
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "active"
    assert confirm_res.json()["confirmed_by_doer_at"] is not None

    # Check gig status is now InProgress
    gig_check = await poster_client.get(f"/api/v1/gigs/{gig_id}")
    assert gig_check.json()["status"] == "InProgress"
