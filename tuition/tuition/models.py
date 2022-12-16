import uuid

from django.db import models
from django.core.validators import MinValueValidator
from django_prometheus.models import ExportModelOperationsMixin


# Create your models here.
class TuitionFee(ExportModelOperationsMixin('tuitionfee'), models.Model):
    degree_id = models.UUIDField(default=uuid.uuid4)
    student_id = models.PositiveBigIntegerField()
    amount = models.DecimalField(
        validators=[MinValueValidator(1.0)], decimal_places=2, max_digits=6)
    deadline = models.DateField()
    is_paid = models.BooleanField(default=False)
