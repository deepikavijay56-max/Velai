import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# Ensure backend directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import select, delete
from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.state_machine import GigStatus
from app.models.user import User, UserRole, UserSkill, Skill
from app.models.organization import Organization, OrgMember, OrgType, OrgVerificationStatus
from app.models.gig import Gig, GigSkill
from app.models.application import Application, ApplicationStatus
from app.models.contract import Contract, Deliverable, PaymentRecord, ContractStatus, DeliverableStatus
from app.models.message import Message
from app.models.review import Review
from app.models.notification import Notification, NotificationPref


async def seed_database():
    print("=" * 65)
    print(f" VELAI SEED SCRIPT — Populating data for {settings.COLLEGE_NAME}")
    print("=" * 65)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Clean existing records for idempotent runs
        print("\n[1/6] Cleaning existing records...")
        await session.execute(delete(Review))
        await session.execute(delete(PaymentRecord))
        await session.execute(delete(Deliverable))
        await session.execute(delete(Contract))
        await session.execute(delete(Application))
        await session.execute(delete(Message))
        await session.execute(delete(GigSkill))
        await session.execute(delete(Gig))
        await session.execute(delete(OrgMember))
        await session.execute(delete(Organization))
        await session.execute(delete(UserSkill))
        await session.execute(delete(Notification))
        await session.execute(delete(NotificationPref))
        await session.execute(delete(User))
        await session.execute(delete(Skill))
        await session.commit()

        # 2. Seed Skills Catalog
        print("[2/6] Seeding standard skill definitions...")
        catalog_skills = [
            ("Figma", "Design"),
            ("Photoshop", "Design"),
            ("Illustrator", "Design"),
            ("Poster Design", "Design"),
            ("UI/UX Design", "Design"),
            ("Video Editing", "Video & Audio"),
            ("Premiere Pro", "Video & Audio"),
            ("After Effects", "Video & Audio"),
            ("Reels Creation", "Video & Audio"),
            ("Python", "Web & Code"),
            ("React", "Web & Code"),
            ("Node.js", "Web & Code"),
            ("TailwindCSS", "Web & Code"),
            ("Flutter", "Web & Code"),
            ("SolidWorks", "Engineering"),
            ("3D Modeling", "Engineering"),
            ("Event Photography", "Photography"),
            ("Lightroom", "Photography"),
            ("Technical Writing", "Writing"),
            ("Copywriting", "Writing"),
            ("Calculus Tutoring", "Tutoring"),
            ("Data Structures Tutoring", "Tutoring"),
            ("Excel & Sheets", "Data"),
            ("Stage Management", "Events & Ops"),
        ]
        for name, category in catalog_skills:
            session.add(Skill(name=name, category=category))
        await session.commit()

        # 3. Seed 30 Users (1 Admin, 4 Staff, 25 Students)
        print("[3/6] Seeding 30 users (1 Admin, 4 Staff, 25 Students)...")
        
        users_data: List[Dict[str, Any]] = [
            # 1 Admin
            {
                "email": settings.ADMIN_EMAIL,
                "name": "Dr. Sundaramurthy K",
                "department": "Dean Administration",
                "year": None,
                "role": UserRole.ADMIN,
                "reputation": 5.0,
            },
            # 4 Staff Members
            {
                "email": "hod.cse@psgtech.ac.in",
                "name": "Dr. K. Jayashree",
                "department": "Computer Science & Engineering",
                "year": None,
                "role": UserRole.STAFF,
                "reputation": 5.0,
            },
            {
                "email": "faculty.mech@psgtech.ac.in",
                "name": "Prof. R. Venkatesh",
                "department": "Mechanical Engineering",
                "year": None,
                "role": UserRole.STAFF,
                "reputation": 4.9,
            },
            {
                "email": "arts.advisor@psgtech.ac.in",
                "name": "Dr. M. Senthil",
                "department": "Humanities & Cultural Council",
                "year": None,
                "role": UserRole.STAFF,
                "reputation": 4.8,
            },
            {
                "email": "placement.cell@psgtech.ac.in",
                "name": "Prof. S. Anand",
                "department": "Career & Placement Division",
                "year": None,
                "role": UserRole.STAFF,
                "reputation": 5.0,
            },
            # 25 Students
            {
                "email": "arun.kumar@psgtech.ac.in",
                "name": "Arun Kumar",
                "department": "Mechanical Engineering",
                "year": 4,
                "role": UserRole.STUDENT,
                "reputation": 4.9,
                "skills": [("SolidWorks", "expert"), ("3D Modeling", "expert"), ("Poster Design", "intermediate")],
            },
            {
                "email": "priya.sundaram@psgtech.ac.in",
                "name": "Priya Sundaram",
                "department": "Computer Science & Engineering",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 5.0,
                "skills": [("Figma", "expert"), ("UI/UX Design", "expert"), ("Poster Design", "expert")],
            },
            {
                "email": "kavitha.raman@psgtech.ac.in",
                "name": "Kavitha Raman",
                "department": "Information Technology",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.8,
                "skills": [("React", "expert"), ("TailwindCSS", "expert"), ("Node.js", "intermediate")],
            },
            {
                "email": "dinesh.karthik@psgtech.ac.in",
                "name": "Dinesh Karthik",
                "department": "Electronics & Communication",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.7,
                "skills": [("Video Editing", "expert"), ("Premiere Pro", "expert"), ("Reels Creation", "expert")],
            },
            {
                "email": "meera.nair@psgtech.ac.in",
                "name": "Meera Nair",
                "department": "Electrical & Electronics",
                "year": 4,
                "role": UserRole.STUDENT,
                "reputation": 5.0,
                "skills": [("Event Photography", "expert"), ("Lightroom", "expert"), ("Photoshop", "intermediate")],
            },
            {
                "email": "sanjay.raghavan@psgtech.ac.in",
                "name": "Sanjay Raghavan",
                "department": "Computer Science & Engineering",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.9,
                "skills": [("Python", "expert"), ("Data Structures Tutoring", "expert"), ("React", "intermediate")],
            },
            {
                "email": "ananya.sharma@psgtech.ac.in",
                "name": "Ananya Sharma",
                "department": "Biotechnology",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.6,
                "skills": [("Technical Writing", "expert"), ("Copywriting", "expert"), ("Excel & Sheets", "intermediate")],
            },
            {
                "email": "rahul.varma@psgtech.ac.in",
                "name": "Rahul Varma",
                "department": "Robotics & Automation",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.8,
                "skills": [("Python", "expert"), ("SolidWorks", "intermediate"), ("Excel & Sheets", "expert")],
            },
            {
                "email": "swetha.m@psgtech.ac.in",
                "name": "Swetha M",
                "department": "Computer Science & Engineering",
                "year": 4,
                "role": UserRole.STUDENT,
                "reputation": 5.0,
                "skills": [("Figma", "expert"), ("Illustrator", "expert"), ("Poster Design", "expert")],
            },
            {
                "email": "karthik.subramanian@psgtech.ac.in",
                "name": "Karthik Subramanian",
                "department": "Civil Engineering",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.5,
                "skills": [("Stage Management", "expert"), ("Poster Design", "beginner")],
            },
            {
                "email": "pooja.reddy@psgtech.ac.in",
                "name": "Pooja Reddy",
                "department": "Information Technology",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.9,
                "skills": [("React", "expert"), ("Flutter", "intermediate"), ("TailwindCSS", "expert")],
            },
            {
                "email": "vikram.aditya@psgtech.ac.in",
                "name": "Vikram Aditya",
                "department": "Mechanical Engineering",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.7,
                "skills": [("SolidWorks", "expert"), ("Calculus Tutoring", "expert")],
            },
            {
                "email": "harini.b@psgtech.ac.in",
                "name": "Harini B",
                "department": "Fashion Technology",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.8,
                "skills": [("Illustrator", "expert"), ("Photoshop", "expert"), ("Poster Design", "expert")],
            },
            {
                "email": "ashwin.prasad@psgtech.ac.in",
                "name": "Ashwin Prasad",
                "department": "Electronics & Communication",
                "year": 4,
                "role": UserRole.STUDENT,
                "reputation": 5.0,
                "skills": [("After Effects", "expert"), ("Premiere Pro", "expert"), ("Video Editing", "expert")],
            },
            {
                "email": "divya.krishnan@psgtech.ac.in",
                "name": "Divya Krishnan",
                "department": "Biotechnology",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.6,
                "skills": [("Excel & Sheets", "expert"), ("Technical Writing", "intermediate")],
            },
            {
                "email": "naveen.kumar@psgtech.ac.in",
                "name": "Naveen Kumar",
                "department": "Production Engineering",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.7,
                "skills": [("Event Photography", "intermediate"), ("Lightroom", "intermediate")],
            },
            {
                "email": "shreya.patel@psgtech.ac.in",
                "name": "Shreya Patel",
                "department": "Computer Science & Engineering",
                "year": 1,
                "role": UserRole.STUDENT,
                "reputation": 5.0,
                "skills": [("Python", "intermediate"), ("Figma", "intermediate")],
            },
            {
                "email": "vijay.balaji@psgtech.ac.in",
                "name": "Vijay Balaji",
                "department": "Information Technology",
                "year": 4,
                "role": UserRole.STUDENT,
                "reputation": 4.9,
                "skills": [("React", "expert"), ("Node.js", "expert"), ("TailwindCSS", "expert")],
            },
            {
                "email": "sneha.iyer@psgtech.ac.in",
                "name": "Sneha Iyer",
                "department": "Electrical & Electronics",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.7,
                "skills": [("Calculus Tutoring", "expert"), ("Excel & Sheets", "intermediate")],
            },
            {
                "email": "rohit.sen@psgtech.ac.in",
                "name": "Rohit Sen",
                "department": "Mechanical Engineering",
                "year": 1,
                "role": UserRole.STUDENT,
                "reputation": 5.0,
                "skills": [("Poster Design", "intermediate"), ("Reels Creation", "intermediate")],
            },
            {
                "email": "keerthana.v@psgtech.ac.in",
                "name": "Keerthana V",
                "department": "Biotechnology",
                "year": 4,
                "role": UserRole.STUDENT,
                "reputation": 4.8,
                "skills": [("Copywriting", "expert"), ("Technical Writing", "expert")],
            },
            {
                "email": "manoj.prabhakar@psgtech.ac.in",
                "name": "Manoj Prabhakar",
                "department": "Robotics & Automation",
                "year": 2,
                "role": UserRole.STUDENT,
                "reputation": 4.6,
                "skills": [("Python", "intermediate"), ("SolidWorks", "intermediate")],
            },
            {
                "email": "bhavani.s@psgtech.ac.in",
                "name": "Bhavani S",
                "department": "Electronics & Communication",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.9,
                "skills": [("Figma", "expert"), ("UI/UX Design", "intermediate")],
            },
            {
                "email": "gautam.ramesh@psgtech.ac.in",
                "name": "Gautam Ramesh",
                "department": "Civil Engineering",
                "year": 3,
                "role": UserRole.STUDENT,
                "reputation": 4.5,
                "skills": [("Stage Management", "expert"), ("Event Photography", "intermediate")],
            },
            {
                "email": "cafe.owner@psgtech.ac.in",
                "name": "R. Murugesan",
                "department": "Campus Commercial Enterprises",
                "year": None,
                "role": UserRole.STAFF,
                "reputation": 5.0,
                "skills": [],
            },
        ]

        created_users: Dict[str, User] = {}
        for u in users_data:
            user = User(
                college_id=settings.COLLEGE_ID,
                college_email=u["email"],
                name=u["name"],
                department=u["department"],
                year=u["year"],
                role=u["role"],
                reputation=u["reputation"],
                availability={"status": "available", "hours_per_week": 15},
            )
            session.add(user)
            await session.flush()
            created_users[u["email"]] = user

            # Attach skills if student
            if "skills" in u:
                for skill_name, level in u["skills"]:
                    user_skill = UserSkill(
                        user_id=user.id,
                        skill_name=skill_name,
                        level=level,
                        sample_links=[f"https://portfolio.velai.campus/{user.name.lower().replace(' ', '.')}/{skill_name.lower().replace(' ', '-')}"]
                    )
                    session.add(user_skill)

            # Notification preferences
            pref = NotificationPref(
                user_id=user.id,
                muted_topics=[],
                daily_count=0,
                last_count_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            )
            session.add(pref)

        await session.commit()

        # 4. Seed 5 Organizations (3 Clubs, 1 Department, 1 Business)
        print("[4/6] Seeding 5 organizations...")
        orgs_data = [
            {
                "name": "Coding Club (CSI Student Chapter)",
                "type": OrgType.CLUB,
                "description": "Premier programming and developer society conducting college hackathons, bootcamps and tech events.",
                "owner_email": "arun.kumar@psgtech.ac.in",
                "verified_status": OrgVerificationStatus.APPROVED,
                "logo_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=150",
            },
            {
                "name": "Department of Computer Science & Engineering",
                "type": OrgType.DEPARTMENT,
                "description": "Academic department hosting national symposia, research projects, and departmental initiatives.",
                "owner_email": "hod.cse@psgtech.ac.in",
                "verified_status": OrgVerificationStatus.APPROVED,
                "logo_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=150",
            },
            {
                "name": "Fine Arts & Media Club",
                "type": OrgType.CLUB,
                "description": "Student creators club driving campus visual identity, film festivals, fest banners, and photography.",
                "owner_email": "swetha.m@psgtech.ac.in",
                "verified_status": OrgVerificationStatus.APPROVED,
                "logo_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=150",
            },
            {
                "name": "Robotics & Automation Society",
                "type": OrgType.CLUB,
                "description": "Hardware and robotics enthusiasts competing in national bot challenges and aeromodelling.",
                "owner_email": "rahul.varma@psgtech.ac.in",
                "verified_status": OrgVerificationStatus.APPROVED,
                "logo_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=150",
            },
            {
                "name": "Campus Co-op Bookstore & Cafe",
                "type": OrgType.BUSINESS,
                "description": "Approved student bookstore, stationery supplier and cafeteria operating on campus.",
                "owner_email": "cafe.owner@psgtech.ac.in",
                "verified_status": OrgVerificationStatus.APPROVED,
                "logo_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=150",
            },
        ]

        created_orgs: Dict[str, Organization] = {}
        for od in orgs_data:
            owner = created_users[od["owner_email"]]
            org = Organization(
                college_id=settings.COLLEGE_ID,
                name=od["name"],
                type=od["type"],
                description=od["description"],
                verified_status=od["verified_status"],
                owner_id=owner.id,
                logo_url=od["logo_url"],
            )
            session.add(org)
            await session.flush()
            created_orgs[od["name"]] = org

            member = OrgMember(org_id=org.id, user_id=owner.id, role="owner")
            session.add(member)

        await session.commit()

        # 5. Seed 15 Gigs across Lifecycle States
        print("[5/6] Seeding 15 varied gigs across lifecycle states (Open, InProgress, Delivered, Completed, Flagged)...")
        now = datetime.now(timezone.utc)

        gigs_data = [
            # 1. Open
            {
                "title": "Design Cultural Fest Teaser Poster & Instagram Banner",
                "category": "Design",
                "description": "Need an energetic and modern poster design for 'Varnam 2026', our annual cultural fest. Must follow dark neon theme with bold typography.",
                "deliverables": ["Figma source file with components", "A3 printable PDF (300dpi)", "Instagram vertical story (1080x1920)"],
                "budget_min": 1500,
                "budget_max": 2500,
                "deadline": now + timedelta(days=12),
                "revisions": 2,
                "org": "Fine Arts & Media Club",
                "poster_email": "swetha.m@psgtech.ac.in",
                "skills": ["Figma", "Poster Design", "Photoshop"],
                "status": GigStatus.Open,
            },
            # 2. Open
            {
                "title": "Build Department Alumni Registration Webpage",
                "category": "Web & Code",
                "description": "Looking for a clean, responsive single-page landing site for alumni reunion registration. Needs form validation and export to CSV.",
                "deliverables": ["Responsive React/Next.js page", "API integration for Google Sheets/CSV export", "Clean Git repository"],
                "budget_min": 3000,
                "budget_max": 4800,
                "deadline": now + timedelta(days=20),
                "revisions": 2,
                "org": "Department of Computer Science & Engineering",
                "poster_email": "hod.cse@psgtech.ac.in",
                "skills": ["React", "TailwindCSS", "Node.js"],
                "status": GigStatus.Open,
            },
            # 3. Open
            {
                "title": "Edit 30-Second Instagram Reel for Hackathon Launch",
                "category": "Video & Audio",
                "description": "Cut raw video footage from previous year's hackathon into a high-energy 30-second promo reel with sound effects, captions, and motion graphics.",
                "deliverables": ["Full HD 1080x1920 MP4 video", "Premiere Pro / After Effects project archive"],
                "budget_min": 1200,
                "budget_max": 2200,
                "deadline": now + timedelta(days=7),
                "revisions": 2,
                "org": "Coding Club (CSI Student Chapter)",
                "poster_email": "arun.kumar@psgtech.ac.in",
                "skills": ["Premiere Pro", "After Effects", "Reels Creation"],
                "status": GigStatus.Open,
            },
            # 4. Open
            {
                "title": "Event Photography for Intra-College Sports Meet",
                "category": "Photography",
                "description": "Need a student photographer with a DSLR/mirrorless camera to cover the athletics meet and basketball finals over two afternoons.",
                "deliverables": ["Minimum 60 edited high-res action shots", "Google Drive link with raw + edited JPEGs"],
                "budget_min": 2000,
                "budget_max": 3500,
                "deadline": now + timedelta(days=14),
                "revisions": 1,
                "org": "Fine Arts & Media Club",
                "poster_email": "swetha.m@psgtech.ac.in",
                "skills": ["Event Photography", "Lightroom"],
                "status": GigStatus.Open,
            },
            # 5. Open
            {
                "title": "Tutor First-Year Mechanical Students in Engineering Mechanics",
                "category": "Tutoring",
                "description": "Conduct three 90-minute evening tutoring sessions on static equilibrium, trusses, and friction for first-year Mech students prior to midterms.",
                "deliverables": ["3 classroom/online review sessions", "One-page handwritten formula sheets for students"],
                "budget_min": 1200,
                "budget_max": 1800,
                "deadline": now + timedelta(days=10),
                "revisions": 1,
                "org": None,
                "poster_email": "faculty.mech@psgtech.ac.in",
                "skills": ["Calculus Tutoring"],
                "status": GigStatus.Open,
            },
            # 6. Open
            {
                "title": "Design Minimalist Menu Card & Loyalty Stickers for Campus Cafe",
                "category": "Design",
                "description": "Campus Co-op Cafe is revamping its snack menu and student loyalty card. Need clean print-ready typography and coffee bean motifs.",
                "deliverables": ["Print-ready PDF menu card", "Round 50mm sticker design in vector format"],
                "budget_min": 1000,
                "budget_max": 1800,
                "deadline": now + timedelta(days=15),
                "revisions": 2,
                "org": "Campus Co-op Bookstore & Cafe",
                "poster_email": "cafe.owner@psgtech.ac.in",
                "skills": ["Illustrator", "Poster Design", "Photoshop"],
                "status": GigStatus.Open,
            },
            # 7. Open
            {
                "title": "Python Script to Scrape and Clean Robotics Telemetry Data",
                "category": "Web & Code",
                "description": "We have CSV logs from ultrasonic sensors and IMUs that need a cleaning script with outliers removed and plotted into Matplotlib graphs.",
                "deliverables": ["Tested Python script (.py)", "Requirements file and sample Jupyter notebook output"],
                "budget_min": 1800,
                "budget_max": 3000,
                "deadline": now + timedelta(days=8),
                "revisions": 1,
                "org": "Robotics & Automation Society",
                "poster_email": "rahul.varma@psgtech.ac.in",
                "skills": ["Python", "Excel & Sheets"],
                "status": GigStatus.Open,
            },
            # 8. Open
            {
                "title": "Content Writer for Technical Symposium Sponsorship Brochure",
                "category": "Writing & Content",
                "description": "Write persuasive copy for our national symposium sponsorship kit. Must explain delegate profile, footfall, and sponsorship tiers.",
                "deliverables": ["4-page brochure copy in Google Docs", "Executive summary blurb for emails"],
                "budget_min": 1000,
                "budget_max": 1700,
                "deadline": now + timedelta(days=11),
                "revisions": 2,
                "org": "Coding Club (CSI Student Chapter)",
                "poster_email": "arun.kumar@psgtech.ac.in",
                "skills": ["Technical Writing", "Copywriting"],
                "status": GigStatus.Open,
            },
            # 9. Open
            {
                "title": "Stage Operations & Sound Console Coordinator for Annual Day",
                "category": "Events & Ops",
                "description": "Experienced audio/stage coordinator needed for rehearsal and main stage audio mixing during college day cultural evening.",
                "deliverables": ["Coordination during sound check and 4-hour live event"],
                "budget_min": 1500,
                "budget_max": 2500,
                "deadline": now + timedelta(days=18),
                "revisions": 1,
                "org": None,
                "poster_email": "arts.advisor@psgtech.ac.in",
                "skills": ["Stage Management"],
                "status": GigStatus.Open,
            },
            # 10. Open
            {
                "title": "Design 3D Printable Chassis Bracket in SolidWorks",
                "category": "Engineering",
                "description": "Create a lightweight mounting bracket for our autonomous line-following bot. Need STEP and STL files ready for campus 3D printer.",
                "deliverables": ["SolidWorks part file (.sldprt)", "Exported 3D print ready STL file"],
                "budget_min": 1500,
                "budget_max": 2400,
                "deadline": now + timedelta(days=9),
                "revisions": 2,
                "org": "Robotics & Automation Society",
                "poster_email": "rahul.varma@psgtech.ac.in",
                "skills": ["SolidWorks", "3D Modeling"],
                "status": GigStatus.Open,
            },
            # 11. InProgress (with active contract, doer, double confirmation, and chat)
            {
                "title": "Redesign Department AI & Research Lab Logo",
                "category": "Design",
                "description": "Create a vector logo representing our department's new Artificial Intelligence and Computing laboratory.",
                "deliverables": ["Vector SVG and AI master file", "Transparent PNGs in color, white, and dark mode"],
                "budget_min": 1500,
                "budget_max": 2200,
                "deadline": now + timedelta(days=6),
                "revisions": 2,
                "org": "Department of Computer Science & Engineering",
                "poster_email": "hod.cse@psgtech.ac.in",
                "doer_email": "priya.sundaram@psgtech.ac.in",
                "skills": ["Illustrator", "UI/UX Design"],
                "status": GigStatus.InProgress,
                "contract_price": 2000,
            },
            # 12. Delivered (with submitted deliverable waiting for poster review)
            {
                "title": "Animated Motion Graphics Intro for College YouTube Channel",
                "category": "Video & Audio",
                "description": "Create a 5-second 3D motion graphics sting with the college emblem and sound effect for departmental video series.",
                "deliverables": ["4K 60fps ProRes / MP4 render with transparent alpha"],
                "budget_min": 2000,
                "budget_max": 3200,
                "deadline": now + timedelta(days=4),
                "revisions": 2,
                "org": "Fine Arts & Media Club",
                "poster_email": "swetha.m@psgtech.ac.in",
                "doer_email": "ashwin.prasad@psgtech.ac.in",
                "skills": ["After Effects", "Premiere Pro", "Video Editing"],
                "status": GigStatus.Delivered,
                "contract_price": 2800,
            },
            # 13. Completed (Approved, UPI paid/received recorded, 5-star two-way reviews)
            {
                "title": "Create Digital Certificate Template in Figma",
                "category": "Design",
                "description": "Design an elegant, printable certificate template for workshop participants with dynamic name placeholders.",
                "deliverables": ["Figma reusable components", "High-res PDF vector template"],
                "budget_min": 1000,
                "budget_max": 1800,
                "deadline": now - timedelta(days=5),
                "revisions": 1,
                "org": "Coding Club (CSI Student Chapter)",
                "poster_email": "arun.kumar@psgtech.ac.in",
                "doer_email": "priya.sundaram@psgtech.ac.in",
                "skills": ["Figma", "Poster Design"],
                "status": GigStatus.Completed,
                "contract_price": 1600,
            },
            # 14. Completed (Approved, UPI recorded, reviews)
            {
                "title": "Format IEEE Conference Proceedings Spreadsheet & Authors Index",
                "category": "Data",
                "description": "Organize 85 submitted research paper titles, track numbers, and reviewer ratings into standard IEEE Excel format.",
                "deliverables": ["Cleaned Excel workbook with pivot summary"],
                "budget_min": 1200,
                "budget_max": 2000,
                "deadline": now - timedelta(days=10),
                "revisions": 1,
                "org": "Department of Computer Science & Engineering",
                "poster_email": "hod.cse@psgtech.ac.in",
                "doer_email": "divya.krishnan@psgtech.ac.in",
                "skills": ["Excel & Sheets", "Technical Writing"],
                "status": GigStatus.Completed,
                "contract_price": 1800,
            },
            # 15. Flagged for Academic Dishonesty (Testing Admin Moderation Queue)
            {
                "title": "Urgent: Write my thermodynamics assignment and solve exam questions",
                "category": "Writing & Content",
                "description": "Looking for someone to do my physics homework, solve my final exam questions, and write my lab record copy before Monday.",
                "deliverables": ["Handwritten assignment answers"],
                "budget_min": 1500,
                "budget_max": 3000,
                "deadline": now + timedelta(days=2),
                "revisions": 1,
                "org": None,
                "poster_email": "rohit.sen@psgtech.ac.in",
                "skills": ["Calculus Tutoring"],
                "status": GigStatus.Open,
                "is_flagged": True,
                "flag_reason": "Contains restricted academic terms: assignment, exam, homework, solve my exam, lab record copy",
            },
        ]

        for gd in gigs_data:
            poster = created_users[gd["poster_email"]]
            org_id = created_orgs[gd["org"]].id if gd.get("org") else None

            gig = Gig(
                college_id=settings.COLLEGE_ID,
                org_id=org_id,
                poster_id=poster.id,
                title=gd["title"],
                category=gd["category"],
                description=gd["description"],
                deliverables=gd["deliverables"],
                budget_min=gd["budget_min"],
                budget_max=gd["budget_max"],
                deadline=gd["deadline"],
                revisions=gd["revisions"],
                status=gd["status"],
                is_flagged_academic=gd.get("is_flagged", False),
                flag_reason=gd.get("flag_reason"),
            )
            session.add(gig)
            await session.flush()

            # Attach skills
            for s_name in gd["skills"]:
                session.add(GigSkill(gig_id=gig.id, skill_name=s_name))

            # If gig is InProgress, Delivered, or Completed, build out the contract lifecycle!
            if gd["status"] in (GigStatus.InProgress, GigStatus.Delivered, GigStatus.Completed):
                doer = created_users[gd["doer_email"]]

                # 1. Application
                app = Application(
                    gig_id=gig.id,
                    user_id=doer.id,
                    pitch=f"Hello! I am a {doer.department} student with proven experience. Here is my previous work.",
                    sample_url=f"https://portfolio.velai.campus/{doer.name.lower().replace(' ', '.')}",
                    proposed_price=gd["contract_price"],
                    proposed_days=4,
                    status=ApplicationStatus.ACCEPTED,
                )
                session.add(app)
                await session.flush()

                # 2. Contract
                confirmed_at = now - timedelta(days=3)
                contract_status = (
                    ContractStatus.COMPLETED
                    if gd["status"] == GigStatus.Completed
                    else ContractStatus.ACTIVE
                )
                contract = Contract(
                    college_id=settings.COLLEGE_ID,
                    gig_id=gig.id,
                    poster_id=poster.id,
                    doer_id=doer.id,
                    agreed_price=gd["contract_price"],
                    agreed_deadline=gd["deadline"],
                    agreed_revisions=gd["revisions"],
                    revisions_used=0,
                    confirmed_by_poster_at=confirmed_at,
                    confirmed_by_doer_at=confirmed_at,
                    status=contract_status,
                )
                session.add(contract)
                await session.flush()

                # 3. Chat Messages
                msg1 = Message(
                    gig_id=gig.id,
                    sender_id=poster.id,
                    body=f"Hi {doer.name.split()[0]}! Thanks for taking up this gig. Feel free to ask if you need brand assets.",
                )
                msg2 = Message(
                    gig_id=gig.id,
                    sender_id=doer.id,
                    body="Thanks! I have started work on the draft and will submit the preview shortly.",
                )
                session.add_all([msg1, msg2])

                # 4. Deliverables if Delivered or Completed
                if gd["status"] in (GigStatus.Delivered, GigStatus.Completed):
                    deliv_status = (
                        DeliverableStatus.ACCEPTED
                        if gd["status"] == GigStatus.Completed
                        else DeliverableStatus.SUBMITTED
                    )
                    deliverable = Deliverable(
                        contract_id=contract.id,
                        file_url=f"https://storage.velai.campus/deliverables/{gig.id}/v1-final.zip",
                        note="Completed deliverable according to all specified requirements. Please review!",
                        version=1,
                        status=deliv_status,
                    )
                    session.add(deliverable)

                # 5. Payment & Reviews if Completed
                if gd["status"] == GigStatus.Completed:
                    pay = PaymentRecord(
                        contract_id=contract.id,
                        amount=gd["contract_price"],
                        method="upi_direct",
                        poster_marked_paid=True,
                        poster_marked_paid_at=now - timedelta(days=1),
                        doer_marked_received=True,
                        doer_marked_received_at=now - timedelta(days=1),
                        status="completed",
                    )
                    session.add(pay)

                    # Poster reviews Doer
                    rev1 = Review(
                        contract_id=contract.id,
                        reviewer_id=poster.id,
                        reviewee_id=doer.id,
                        rating=5,
                        comment="Exceptional attention to detail and completed ahead of deadline!",
                        tags=["fast", "creative", "reliable"],
                    )
                    # Doer reviews Poster
                    rev2 = Review(
                        contract_id=contract.id,
                        reviewer_id=doer.id,
                        reviewee_id=poster.id,
                        rating=5,
                        comment="Super clear brief, great communication and prompt payment.",
                        tags=["clear brief", "prompt payment"],
                    )
                    session.add_all([rev1, rev2])
                    doer.completed_gigs_count += 1

        await session.commit()

        # 6. Verify seed counts
        print("\n[6/6] Verifying seeded database counts...")
        u_count = (await session.execute(select(User))).scalars().all()
        o_count = (await session.execute(select(Organization))).scalars().all()
        g_count = (await session.execute(select(Gig))).scalars().all()
        c_count = (await session.execute(select(Contract))).scalars().all()
        f_count = (await session.execute(select(Gig).where(Gig.is_flagged_academic == True))).scalars().all()

        print(f" -> Total Users: {len(u_count)} (Expected: 30)")
        print(f" -> Total Organizations: {len(o_count)} (Expected: 5)")
        print(f" -> Total Gigs: {len(g_count)} (Expected: 15)")
        print(f" -> Total Contracts: {len(c_count)} (3 lifecycle demo contracts: InProgress, Delivered, Completed)")
        print(f" -> Flagged Gigs in Moderation Queue: {len(f_count)} (1 academic dishonesty test)")

        print("\n" + "=" * 65)
        print(" SEED DATA LOADED SUCCESSFULLY IN ONE COMMAND!")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_database())
