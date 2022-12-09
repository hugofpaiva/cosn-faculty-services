from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class TuitionFee(models.Model):
    name = models.CharField(max_length=30)
    degree_id = models.PositiveBigIntegerField()
    student_id = models.PositiveBigIntegerField()
    amount = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1.0)])
    deadline = models.DateField()
    is_paid = models.BooleanField()
    