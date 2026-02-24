from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50)
    description = models.TextField()


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    year = models.CharField(max_length=50)


class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()


class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    issuer = models.CharField(max_length=100)
# Create your models here.
