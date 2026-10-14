from django.db import models
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimestampedModel):
    name = models.CharField(max_length=120, default="Nimesh Rai")
    title = models.CharField(max_length=180, default="Python Developer | Backend Engineer")
    intro = models.CharField(max_length=320, default="I build practical software, reliable APIs, and data-driven tools.")
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, default="India")
    email = models.EmailField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.name


class Project(TimestampedModel):
    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        ACTIVE = "ACTIVE", "Active"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.CharField(max_length=60, default="PYTHON", db_index=True)
    short_description = models.CharField(max_length=280)
    description = models.TextField(blank=True)
    problem = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    architecture = models.TextField(blank=True)
    tech_stack = models.JSONField(default=list, blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("-is_featured", "display_order", "title")
        indexes = [models.Index(fields=("is_published", "is_featured", "display_order"))]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:160] or "project"
            candidate, suffix = base, 2
            while Project.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate, suffix = f"{base}-{suffix}", suffix + 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SkillCategory(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "name")
        verbose_name_plural = "Skill categories"

    def __str__(self):
        return self.name


class Skill(TimestampedModel):
    category = models.ForeignKey(SkillCategory, related_name="skills", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    proficiency = models.PositiveSmallIntegerField(default=60)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "name")
        constraints = [models.UniqueConstraint(fields=("category", "name"), name="unique_skill_per_category")]

    def __str__(self):
        return self.name


class ContactMessage(TimestampedModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField(max_length=100000)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ("is_read", "-created_at")

    def __str__(self):
        return f"{self.subject or 'Message'} from {self.name}"
