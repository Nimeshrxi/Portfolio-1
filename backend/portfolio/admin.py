from django.contrib import admin
from .models import ContactMessage, Profile, Project, Skill, SkillCategory


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "updated_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "is_featured", "is_published", "display_order")
    list_filter = ("category", "status", "is_featured", "is_published")
    search_fields = ("title", "short_description", "description", "tech_stack")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_featured", "is_published", "display_order")
    ordering = ("display_order", "title")


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order")
    inlines = (SkillInline,)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "updated_at")
