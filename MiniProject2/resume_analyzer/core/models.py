from django.contrib.auth.models import AbstractUser
from django.db import models
from django_mongoengine import Document
from django_mongoengine import fields
from mongoengine import FileField, DictField, FloatField, IntField


class User(AbstractUser):
    ROLE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class JobListing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills_required = models.JSONField()
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'recruiter'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Resume(Document):  # MongoDB model
    user_id = IntField(required=True)
    file = FileField()
    extracted_data = DictField(default=dict)
    score = FloatField(null=True)
    meta = {'db_alias': 'default'}


class Log(models.Model):  # MySQL
    user_id = models.IntegerField()
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
