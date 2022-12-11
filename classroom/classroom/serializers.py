from classroom.models import Classroom, Schedule
from rest_framework import serializers


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only = ['id', 'classroom']


class ClassroomWithScheduleSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Classroom
        exclude = ['faculty_id']
        read_only = ['id']


class ClassroomWithoutScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        exclude = ['faculty_id']
        read_only = ['id', 'name', 'seats']


class ErrorSerializer(serializers.Serializer):
    details = serializers.CharField()
