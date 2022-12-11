from django.db import models
from django_countries.fields import CountryField
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class Location(models.Model):
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],)
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
    )
    country = CountryField()
    address = models.CharField(max_length=250)


class Faculty(models.Model):
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True
    )


class Article(models.Model):
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=30)
    content = models.TextField()
    author = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
