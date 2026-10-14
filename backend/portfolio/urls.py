from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ContactCreateView, ReadOnlyProjectViewSet, contact_form, profile_api, search_api, skills_api

app_name = "portfolio"
router = DefaultRouter()
router.register("projects", ReadOnlyProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", profile_api, name="profile-api"),
    path("skills/", skills_api, name="skills-api"),
    path("search/", search_api, name="search-api"),
    path("contact/", ContactCreateView.as_view(), name="contact-api"),
    path("contact/form/", contact_form, name="contact-form"),
]
