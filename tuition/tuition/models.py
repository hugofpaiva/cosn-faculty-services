from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class TuitionFee(models.Model):
    degree_id = models.PositiveBigIntegerField()
    student_id = models.PositiveBigIntegerField()
    amount = models.DecimalField(
        validators=[MinValueValidator(1.0)], decimal_places=2, max_digits=5)
    deadline = models.DateField()
    is_paid = models.BooleanField(default=False)
