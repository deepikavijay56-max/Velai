import asyncio
import httpx
from app.main import app

async def run_checks():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        print("1. Health Check:", res.status_code, res.json())
        assert res.status_code == 200

        # 2. Auth: Poster (Club lead)
        otp_res = await client.post("/api/v1/auth/request-otp", json={"email": "lead@psgtech.ac.in"})
        poster_otp = otp_res.json()["dev_mock_otp"]
        res = await client.post("/api/v1/auth/verify-otp", json={
            "email": "lead@psgtech.ac.in",
            "otp_code": poster_otp,
            "name": "Arun Kumar",
            "department": "Mechanical",
            "year": 4,
            "role": "student"
        })
        poster_token = res.json()["access_token"]
        poster_headers = {"Authorization": f"Bearer {poster_token}"}
        print("2. Poster authenticated:", res.json()["user"]["name"])

        # 3. Auth: Doer (Freelance student)
        otp_res = await client.post("/api/v1/auth/request-otp", json={"email": "doer@psgtech.ac.in"})
        doer_otp = otp_res.json()["dev_mock_otp"]
        res = await client.post("/api/v1/auth/verify-otp", json={
            "email": "doer@psgtech.ac.in",
            "otp_code": doer_otp,
            "name": "Priya Sundaram",
            "department": "Design",
            "year": 2,
            "role": "student"
        })
        doer_token = res.json()["access_token"]
        doer_headers = {"Authorization": f"Bearer {doer_token}"}
        print("3. Doer authenticated:", res.json()["user"]["name"])

        # 4. Poster creates a gig with max 1 revision
        res = await client.post("/api/v1/gigs", headers=poster_headers, json={
            "title": "Design Freshers Welcome Banner",
            "category": "Design",
            "description": "Create an energetic campus welcome banner for incoming first years.",
            "deliverables": ["Figma source file", "300dpi print banner"],
            "budget_min": 1200,
            "budget_max": 2000,
            "deadline": "2026-11-10T12:00:00Z",
            "revisions": 1,
            "skills": ["Figma", "Banner Design"]
        })
        assert res.status_code == 200
        gig = res.json()
        gig_id = gig["id"]
        print("4. Gig created:", gig_id, "Status:", gig["status"], "Revisions allowed:", gig["revisions"])

        # 5. Doer applies for the gig
        res = await client.post(f"/api/v1/gigs/{gig_id}/apply", headers=doer_headers, json={
            "pitch": "I designed the banners for last year's tech fest. Portfolio attached.",
            "sample_url": "https://portfolio.me/priya",
            "proposed_price": 1800,
            "proposed_days": 3
        })
        assert res.status_code == 200
        app_id = res.json()["id"]
        print("5. Application submitted:", app_id, "Proposed price:", res.json()["proposed_price"])

        # 6. Poster accepts applicant -> creates Contract
        res = await client.post(f"/api/v1/applications/{app_id}/accept", headers=poster_headers)
        assert res.status_code == 200
        contract = res.json()
        contract_id = contract["id"]
        print("6. Poster accepted applicant. Contract ID:", contract_id, "Status:", contract["status"])

        # 7. Doer confirms contract agreement -> triggers Gig state transition to InProgress!
        res = await client.post(f"/api/v1/contracts/{contract_id}/confirm", headers=doer_headers)
        assert res.status_code == 200
        print("7. Doer confirmed agreement. Contract status:", res.json()["status"])

        # Verify gig state is now InProgress
        res = await client.get(f"/api/v1/gigs/{gig_id}", headers=doer_headers)
        assert res.json()["status"] == "InProgress"
        print("   -> Gig state successfully transitioned to: InProgress")

        # 8. Try invalid state transition: Poster attempts to cancel an InProgress gig via cancel endpoint
        res = await client.post(f"/api/v1/gigs/{gig_id}/cancel", headers=poster_headers)
        print("8. Rejection of invalid transition (InProgress -> Cancelled):", res.status_code, res.json()["detail"])
        assert res.status_code == 400

        # 9. Doer delivers work (v1) -> Gig transitions InProgress -> Delivered
        res = await client.post(f"/api/v1/contracts/{contract_id}/deliver", headers=doer_headers, json={
            "file_url": "https://storage.velai.campus/banners/v1-freshers.pdf",
            "note": "Here is the first draft of the welcome banner in 300dpi."
        })
        assert res.status_code == 200
        deliv_id = res.json()["id"]
        print("9. Work delivered (v1). Deliverable status:", res.json()["status"])

        # Check gig status is now Delivered
        res = await client.get(f"/api/v1/gigs/{gig_id}", headers=poster_headers)
        assert res.json()["status"] == "Delivered"
        print("   -> Gig state successfully transitioned to: Delivered")

        # 10. Poster requests revision (Revision 1 of 1) -> Gig transitions Delivered -> InProgress
        res = await client.post(f"/api/v1/deliverables/{deliv_id}/revise", headers=poster_headers, json={
            "revision_reason": "Please make the college logo slightly larger and adjust font contrast."
        })
        assert res.status_code == 200
        print("10. Revision 1 requested. Deliverable status:", res.json()["status"])

        # Check gig status is back to InProgress
        res = await client.get(f"/api/v1/gigs/{gig_id}", headers=poster_headers)
        assert res.json()["status"] == "InProgress"
        print("   -> Gig state successfully transitioned back to: InProgress")

        # 11. Doer delivers revised work (v2) -> Gig transitions InProgress -> Delivered
        res = await client.post(f"/api/v1/contracts/{contract_id}/deliver", headers=doer_headers, json={
            "file_url": "https://storage.velai.campus/banners/v2-freshers.pdf",
            "note": "Adjusted the logo size and sharpened contrast as requested!"
        })
        assert res.status_code == 200
        deliv2_id = res.json()["id"]
        print("11. Work delivered (v2). Version:", res.json()["version"])

        # 12. Poster attempts Revision 2 (when agreed limit was 1) -> REJECTED with revision limit error!
        res = await client.post(f"/api/v1/deliverables/{deliv2_id}/revise", headers=poster_headers, json={
            "revision_reason": "Can you also change the background pattern?"
        })
        print("12. Revision limit enforcement (1/1 reached):", res.status_code, res.json()["detail"])
        assert res.status_code == 400
        assert "Revision limit reached" in res.json()["detail"]

        # 13. Poster approves deliverable -> Gig transitions Delivered -> Completed!
        res = await client.post(f"/api/v1/deliverables/{deliv2_id}/approve", headers=poster_headers)
        assert res.status_code == 200
        print("13. Deliverable approved! Status:", res.json()["status"])

        # Verify gig status is Completed
        res = await client.get(f"/api/v1/gigs/{gig_id}", headers=poster_headers)
        assert res.json()["status"] == "Completed"
        print("   -> Gig state successfully transitioned to: Completed")

        # 14. Poster records UPI payment sent directly outside app
        res = await client.post(f"/api/v1/contracts/{contract_id}/payment/paid", headers=poster_headers)
        assert res.status_code == 200
        print("14. Poster marked paid outside app. Status:", res.json()["poster_marked_paid"])

        # 15. Doer confirms UPI payment received
        res = await client.post(f"/api/v1/contracts/{contract_id}/payment/received", headers=doer_headers)
        assert res.status_code == 200
        print("15. Doer marked received. Payment Status:", res.json()["status"])
        assert res.json()["status"] == "completed"

        # 16. Two-way reviews: Poster reviews Doer
        res = await client.post(f"/api/v1/contracts/{contract_id}/review", headers=poster_headers, json={
            "rating": 5,
            "comment": "Exceptional graphic work, very fast turn around on the revision!",
            "tags": ["fast", "creative", "proactive"]
        })
        assert res.status_code == 200
        print("16. Poster submitted 5-star review for doer")

        # Doer reviews Poster
        res = await client.post(f"/api/v1/contracts/{contract_id}/review", headers=doer_headers, json={
            "rating": 5,
            "comment": "Clear brief and prompt payment right after approval!",
            "tags": ["clear brief", "prompt payment"]
        })
        assert res.status_code == 200
        print("17. Doer submitted 5-star review for poster")

        # Check Doer profile reputation and completed count
        res = await client.get("/api/v1/auth/me", headers=doer_headers)
        print("18. Doer final stats: Completed gigs:", res.json()["completed_gigs_count"], "Reputation:", res.json()["reputation"])
        assert res.json()["completed_gigs_count"] >= 1

        print("\n=======================================================")
        print(" ALL END-TO-END GIG STATE MACHINE CHECKS PASSED 100%!")
        print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(run_checks())
