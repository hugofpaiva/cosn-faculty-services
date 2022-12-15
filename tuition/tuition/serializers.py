import uuid

from tuition.models import TuitionFee
from rest_framework import serializers


class TuitionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuitionFee
        fields = '__all__'
        read_only = ['id']


class CreateTuitionFeeSerializer(serializers.Serializer):
    degree_id = serializers.UUIDField(default=uuid.uuid4)
    student_id = serializers.IntegerField()
    payment_type = serializers.ChoiceField(choices=['MONTHLY', 'ANNUAL'])


class ReceiptParametersSerializer(serializers.Serializer):
    tuition_fee_id = serializers.IntegerField()


class ErrorSerializer(serializers.Serializer):
    details = serializers.CharField()
