from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from portfolio import views

admin.site.site_header = "Nimesh Rai · Portfolio Control Room"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Manage public portfolio content"

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/<slug:slug>/", views.project_detail, name="project-detail"),
    path("admin/", admin.site.urls),
    path("api/portfolio/", include("portfolio.urls")),
    path("health/", RedirectView.as_view(url="/api/portfolio/", permanent=False), name="health"),
]
