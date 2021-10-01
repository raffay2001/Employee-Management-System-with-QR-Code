from django.db import models
from datetime import datetime, timezone
from django.contrib.auth.models import User, auth
import uuid
from django.db.models.deletion import CASCADE
from django.db.models.fields import UUIDField
from django.utils import timezone
import json

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

# MODEL FOR CARD TEMPLATE


class Scan(models.Model):
    my_file = models.ImageField(upload_to="temp_folder")


class CardTemplate(models.Model):
    name = models.CharField(max_length=255)
    html_file_name = models.CharField(max_length=255)

    def full_path(self):
        return f"id-cards/{self.html_file_name}"

    def __str__(self):
        return f'{self.name} - {self.html_file_name}'

# MODEL FOR COMPANY ADMIN


class CompanyAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return f'{self.user}'

# Create your models here.
# MODEL FOR COMPANY


class Company(models.Model):
    name = models.CharField(max_length=255)
    tagline = models.CharField(
        max_length=255, default="A place where a character builts.")
    description = models.TextField(max_length=255)
    founded_in = models.IntegerField()
    card_template = models.ForeignKey(CardTemplate, on_delete=models.CASCADE)
    company_admin = models.ForeignKey(CompanyAdmin, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.founded_in}) - Admin: {self.company_admin.user}'

# MODEL FOR EMPLOYEE


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    designation = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255)
    birthday = models.DateField()
    profile_picture = models.ImageField(upload_to="profile_pictures")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    member_since = models.DateTimeField(default=timezone.now)

    def getJson(self):
        data = {
            'id': str(self.id),
            'filename': self.full_name().replace(" ", "-") + "-id-card.pdf",
            'name': self.full_name(),
            'email': self.email,
            'designation': self.designation,
            'profile_picture': str(self.profile_picture),
            'birthday': str(self.birthday),
            'company': {
                'id': self.company.id,
                'name': self.company.name,
                'tagline': self.company.tagline
            },
        }
        return json.dumps(data)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.full_name()} - {self.designation} ({self.company.name})'
