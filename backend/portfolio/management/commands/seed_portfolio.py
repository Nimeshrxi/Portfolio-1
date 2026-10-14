from django.core.management.base import BaseCommand
from portfolio.models import Profile, Project, Skill, SkillCategory


class Command(BaseCommand):
    help = "Create starter portfolio content if the database is empty."

    def handle(self, *args, **options):
        Profile.objects.get_or_create(name="Nimesh Rai", defaults={
            "title": "Python Developer | Backend Engineer | AI & Data Enthusiast",
            "intro": "I build practical software, reliable APIs, and data-driven tools with Python.",
            "bio": "Computer Science graduate focused on Python development, backend engineering, data structures, and clean API design.",
            "location": "Jhansi, India", "email": "nimeshraivibes@gmail.com",
            "github_url": "https://github.com/Nimeshrxi",
        })
        projects = [
            {"title": "OwnMeet", "category": "WEB", "short_description": "Online video conferencing application concept focused on meeting rooms and dependable collaboration flows.", "description": "A web meeting platform exploring room creation, participant flow, and real-time collaboration.", "problem": "Remote collaboration tools need simple entry points and predictable meeting states.", "solution": "A focused meeting experience with room metadata and API-ready backend concepts.", "features": ["Meeting rooms", "Participant flow", "Call controls", "REST-ready domain"], "architecture": "Python domain logic and REST endpoints can own meeting metadata while WebRTC handles media transport.", "tech_stack": ["Python", "Django", "REST APIs", "WebRTC"], "github_url": "https://github.com/Nimeshrxi/ownmeet", "is_featured": True, "display_order": 1, "status": "IN_PROGRESS"},
            {"title": "Formula 1 Management Simulator", "category": "DJANGO", "short_description": "A management-style system for teams, drivers, races, and season standings.", "description": "A relational domain model for Formula 1 entities, race outcomes, standings, and admin workflows.", "problem": "Sports management data needs clear relationships and consistent calculations.", "solution": "A relational model with admin-managed data and API-ready project structure.", "features": ["Team and driver records", "Race calendar", "Points calculations", "Admin workflows"], "architecture": "Django models define entities and relationships; serializers expose stable REST representations.", "tech_stack": ["Python", "Django", "PostgreSQL", "REST APIs"], "github_url": "https://github.com/Nimeshrxi/formula-1-simulator", "is_featured": True, "display_order": 2, "status": "IN_PROGRESS"},
            {"title": "AI-Assisted Trading Research Bot", "category": "AUTOMATION", "short_description": "A Python experiment combining market data, rule-based signals, and automated trade-management research.", "description": "A personal trading automation experiment with logging, strategy modules, and risk-aware execution concepts.", "problem": "Manual analysis can be inconsistent and difficult to audit across repeated decisions.", "solution": "Separate data acquisition, strategy evaluation, risk checks, and execution into testable components.", "features": ["Strategy modules", "Risk checks", "Execution logging", "Trade journal concepts"], "architecture": "Small Python services with explicit interfaces make strategy logic testable independently from broker connectivity.", "tech_stack": ["Python", "OOP", "REST APIs", "Data Analysis"], "github_url": "https://github.com/Nimeshrxi", "is_featured": True, "display_order": 3, "status": "IN_PROGRESS"},
            {"title": "Linux Health Monitor", "category": "DEVOPS", "short_description": "A shell-based operational monitor for service, disk, memory, and scheduled health checks.", "description": "A practical Linux lab project for health reports, systemd service supervision, cron jobs, and log inspection.", "problem": "Small services need quick visibility into service state and basic machine health.", "solution": "Combine scripts, systemd, cron, and persistent logs into a repeatable operations workflow.", "features": ["Disk and memory checks", "Service status", "Cron scheduling", "Log output"], "architecture": "Shell scripts run on Linux and use system tools to gather health signals for logs and reports.", "tech_stack": ["Linux", "Bash", "systemd", "Cron"], "github_url": "https://github.com/Nimeshrxi", "is_featured": False, "display_order": 4, "status": "COMPLETED"},
        ]
        for project in projects:
            Project.objects.update_or_create(title=project["title"], defaults=project)
        skill_data = {
            "Programming & Fundamentals": [("Python", 78), ("Object-oriented programming", 70), ("Data structures & algorithms", 65), ("SQL", 65)],
            "Backend & Data": [("Django", 65), ("Django REST Framework", 55), ("Flask", 45), ("PostgreSQL", 60)],
            "Systems & Tools": [("Ubuntu Linux", 60), ("Git", 55), ("Networking fundamentals", 45), ("Data analysis", 50)],
        }
        for order, (category_name, skills) in enumerate(skill_data.items(), start=1):
            category, _ = SkillCategory.objects.get_or_create(name=category_name, defaults={"display_order": order})
            for skill_order, (name, proficiency) in enumerate(skills, start=1):
                Skill.objects.update_or_create(category=category, name=name, defaults={"proficiency": proficiency, "display_order": skill_order})
        self.stdout.write(self.style.SUCCESS("Starter portfolio content is ready. Review it in /admin/ before publishing."))
