from classroom.models import Classroom, Schedule
from rest_framework import serializers

class ClassroomWithScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        exclude = ['faculty_id']
        read_only = ['id']

class ClassroomWithoutScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        exclude = ['faculty_id']
        read_only = ['id', 'name', 'faculty_id', 'seats']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only = ['id']
