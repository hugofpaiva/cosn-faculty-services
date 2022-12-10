from classroom.models import Classroom, Schedule
from rest_framework import serializers

class ClassroomWithScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = '__all__'
        read_only = ['id', 'schedules']

class ClassroomWithoutScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = '__all__'
        read_only = ['id']
        exclude = ['schedules']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
        read_only = ['id']
