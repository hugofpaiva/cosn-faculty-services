from faculty.models import Faculty, Article, Location
from rest_framework import serializers


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only = ['id']


class FacultySerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = Faculty
        fields = '__all__'
        read_only = ['id']

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        new_location = Location.objects.create(**location_data)
        faculty = Faculty.objects.create(**validated_data, location=new_location)
        return faculty


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        read_only = ['id', 'created_at']


class ErrorSerializer(serializers.Serializer):
    details = serializers.CharField()


class CertificateParametersSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    CERTIFICATE_TYPES = [
        'MASTER_DEGREE_CERTIFICATE',
        'ENROLLMENT_CERTIFICATE',
        'BACHELOR_DEGREE_CERTIFICATE'
    ]
    certificate_type = serializers.ChoiceField(choices=CERTIFICATE_TYPES)
