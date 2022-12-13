from tuition.models import TuitionFee
from rest_framework import serializers


class TuitionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuitionFee
        fields = '__all__'
        read_only = ['id']


class CreateTuitionFeeSerializer(serializers.Serializer):
    degree_id = serializers.models.PositiveBigIntegerField()
    student_id = serializers.models.PositiveBigIntegerField()
    payment_type = serializers.ChoiceField(choices=['MONTHLY', 'ANNUAL'])


class ErrorSerializer(serializers.Serializer):
    details = serializers.CharField()
