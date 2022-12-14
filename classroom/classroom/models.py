import uuid

from django.db import models
from django.core.validators import MinValueValidator


# Create your models here
class Classroom(models.Model):
    name = models.CharField(max_length=30)
    is_available = models.BooleanField(default=True)
    faculty_id = models.PositiveBigIntegerField()
    seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])


class Schedule(models.Model):
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name='schedules')
    course_edition_id = models.CharField(max_length=24)
    start = models.DateTimeField()
    end = models.DateTimeField()
    SCHEDULE_TYPE_CHOICES = (
        ('CL', 'Class'),
        ('EX', 'Exam'),
    )
    type = models.CharField(max_length=2, choices=SCHEDULE_TYPE_CHOICES)
