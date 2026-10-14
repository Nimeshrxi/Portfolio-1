from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.db.models import Count, Max, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import ContactMessage, Profile, Project, Skill, SkillCategory
from .serializers import ContactMessageSerializer, ProfileSerializer, ProjectSerializer, SkillCategorySerializer
from .services.search import ProjectSearchIndex


def _projects():
    return list(Project.objects.filter(is_published=True).values("id", "title", "slug", "category", "short_description", "description", "tech_stack", "is_featured", "status", "github_url", "live_url").order_by("-is_featured", "display_order", "title"))


_SEARCH_INDEX = None
_SEARCH_VERSION = None


def _index():
    """Keep the index in process memory; the index lock is intentionally not pickled."""
    global _SEARCH_INDEX, _SEARCH_VERSION
    aggregate = Project.objects.filter(is_published=True).aggregate(latest=Max("updated_at"), total=Count("id"))
    version = f"{aggregate['total']}:{aggregate['latest']}"
    if _SEARCH_INDEX is None or _SEARCH_VERSION != version:
        _SEARCH_INDEX = ProjectSearchIndex(_projects())
        _SEARCH_VERSION = version
    return _SEARCH_INDEX


@require_GET
def home(request):
    projects = Project.objects.filter(is_published=True).order_by("-is_featured", "display_order", "title")
    query = request.GET.get("q", "").strip()[:100]
    category = request.GET.get("category", "").strip()[:60]
    if query:
        ids = [item["id"] for item in _index().search(query, limit=100)]
        projects = projects.filter(id__in=ids)
    if category:
        projects = projects.filter(category__iexact=category)
    profile = Profile.objects.filter(is_active=True).first()
    skill_categories = SkillCategory.objects.prefetch_related(Prefetch("skills", queryset=Skill.objects.only("id", "category_id", "name", "proficiency", "display_order")))
    categories = Project.objects.filter(is_published=True).values_list("category", flat=True).distinct().order_by("category")
    return render(request, "portfolio/home.html", {"profile": profile, "projects": projects, "skill_categories": skill_categories, "categories": categories, "query": query, "selected_category": category})


@require_GET
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    return render(request, "portfolio/project_detail.html", {"project": project})


class ReadOnlyProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = "slug"
    queryset = Project.objects.filter(is_published=True).order_by("-is_featured", "display_order", "title")
    search_fields = ("title", "short_description", "description", "category")
    filterset_fields = ("category", "status", "is_featured")


class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AnonRateThrottle,)

    def perform_create(self, serializer):
        serializer.save()


@api_view(("GET",))
@permission_classes((permissions.AllowAny,))
def profile_api(request):
    profile = Profile.objects.filter(is_active=True).first()
    if profile is None:
        return Response({"detail": "Profile has not been configured."}, status=status.HTTP_404_NOT_FOUND)
    return Response(ProfileSerializer(profile).data)


@api_view(("GET",))
@permission_classes((permissions.AllowAny,))
def skills_api(request):
    groups = SkillCategory.objects.prefetch_related("skills").all()
    return Response(SkillCategorySerializer(groups, many=True).data)


@api_view(("GET",))
@permission_classes((permissions.AllowAny,))
def search_api(request):
    query = request.query_params.get("q", "").strip()[:100]
    if not query:
        return Response({"count": 0, "results": []})
    try:
        limit = min(max(int(request.query_params.get("limit", 20)), 1), 100)
    except ValueError:
        return Response({"detail": "limit must be an integer between 1 and 100."}, status=status.HTTP_400_BAD_REQUEST)
    results = _index().search(query, limit)
    return Response({"count": len(results), "results": results})


def _contact_email_body(cleaned):
    subject = (cleaned.get("subject") or "Portfolio enquiry").strip() or "Portfolio enquiry"
    message = cleaned["message"].strip()
    return {
        "subject": subject,
        "body": (
            f"Name: {cleaned['name']}\n"
            f"Email: {cleaned['email']}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}"
        ),
    }


def _deliver_contact_email(cleaned):
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        raise ValueError("SMTP credentials are not configured. Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to your .env file.")

    email_details = _contact_email_body(cleaned)
    email = EmailMessage(
        subject=f"[Portfolio Contact] {email_details['subject']}",
        body=email_details["body"],
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[cleaned["email"]],
    )
    email.send(fail_silently=False)


@require_POST
def contact_form(request):
    serializer = ContactMessageSerializer(data=request.POST)
    if serializer.is_valid():
        cleaned = serializer.validated_data
        try:
            _deliver_contact_email(cleaned)
            serializer.save()
            messages.success(request, "Message sent. Thank you for reaching out.")
        except Exception:
            serializer.save()
            messages.error(request, "Message saved, but the email could not be delivered right now. Please check your Gmail app password and SMTP settings, then try again.")
    else:
        messages.error(request, "Please check the form and try again.")
    return redirect("home")
