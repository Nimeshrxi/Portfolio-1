from django.test import TestCase, Client
from django.urls import reverse
from .models import Profile, Project
from .services.search import ProjectSearchIndex


class ProjectSearchIndexTests(TestCase):
    def test_search_matches_title_and_is_case_insensitive(self):
        index = ProjectSearchIndex([{"id": 1, "title": "OwnMeet", "short_description": "video rooms", "tech_stack": ["Python"]}, {"id": 2, "title": "Stock Monitor", "short_description": "market data", "tech_stack": ["Python"]}])
        self.assertEqual(index.search("OWNMEET")[0]["id"], 1)
        self.assertEqual(index.search("market")[0]["id"], 2)

    def test_empty_query_returns_no_results(self):
        self.assertEqual(ProjectSearchIndex([]).search("  "), [])


class PortfolioPageTests(TestCase):
    def setUp(self):
        Profile.objects.create(name="Nimesh Rai", title="Python Developer", intro="Python portfolio")
        Project.objects.create(title="OwnMeet", short_description="A video conferencing project", tech_stack=["Python", "Django"], is_published=True)

    def test_home_loads_without_images(self):
        response = Client().get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nimesh Rai")
        self.assertContains(response, 'src="/_vercel/speed-insights/script.js"')
        self.assertNotContains(response, "<img", html=False)

    def test_project_api_is_read_only(self):
        response = Client().get("/api/portfolio/projects/")
        self.assertEqual(response.status_code, 200)

    def test_search_api_uses_default_limit_when_limit_is_blank(self):
        response = Client().get("/api/portfolio/search/", {"q": "OwnMeet", "limit": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_search_api_rejects_non_integer_limit(self):
        response = Client().get("/api/portfolio/search/", {"q": "OwnMeet", "limit": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "limit must be an integer between 1 and 100.")
