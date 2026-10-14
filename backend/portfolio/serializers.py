from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework import serializers

from .models import ContactMessage, Profile, Project, Skill, SkillCategory

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "name", "title", "intro", "bio", "location", "email", "github_url", "linkedin_url")


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "title", "slug", "category", "short_description", "description", "problem", "solution", "features", "architecture", "tech_stack", "github_url", "live_url", "is_featured", "display_order", "status")
        read_only_fields = fields


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "proficiency", "display_order")


class SkillCategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = SkillCategory
        fields = ("id", "name", "display_order", "skills")


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Please provide a little more detail (at least 10 characters).")
        return value
    
    def create(self, validated_data):
        instance = ContactMessage.objects.create(**validated_data)
        sender_name = validated_data.get("name", "Anonymous")
        sender_email = validated_data.get("email", "No email provided")
        sender_message = validated_data.get("message", "").strip()
        subject = validated_data.get("subject") or f"New Portfolio Message from {sender_name}"
        email_body = (
            "You received a new message on your portfolio website:\n\n"
            f"Name: {sender_name}\n"
            f"Email: {sender_email}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{sender_message}"
        )
        recipient = settings.CONTACT_EMAIL or settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER

        try:
            email = EmailMessage(
                subject=f"[Portfolio Contact] {subject}",
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                to=[recipient],
                reply_to=[sender_email],
            )
            email.send(fail_silently=False)
        except Exception as exc:
            print(f"Email delivery failed: {exc}")
        return instance