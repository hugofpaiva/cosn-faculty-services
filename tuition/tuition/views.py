from django.http import Http404
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from tuition.models import TuitionFee
from tuition.serializers import TuitionFeeSerializer, CreateTuitionFeeSerializer


# Create your views here.
class TuitionFeeListView(generics.GenericAPIView,
                         mixins.ListModelMixin):
    queryset = TuitionFee.objects.all()
    serializer_class = TuitionFeeSerializer
    filterset_fields = {
        'student_id': ['exact'],
        'degree_id': ['exact'],
        'is_paid': ['exact']
    }

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('student_id', None):
            return Response({
                'status': '400',
                'message': 'A student_id is needed to filter the TuitionFees',
            }, status=status.HTTP_400_BAD_REQUEST)

        return self.list(request, *args, **kwargs)


class TuitionFeeDetailsView(generics.GenericAPIView,
                            mixins.RetrieveModelMixin
                            ):
    queryset = TuitionFee.objects.all()
    serializer_class = TuitionFeeSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TuitionFeeCreateView(APIView):
    def post(self, request, format=None):
        serializer = CreateTuitionFeeSerializer(data=request.data)
        if serializer.is_valid():
            # TODO call other service
            now = datetime.now()
            tuition_fees = []

            tuition_fee_1 = TuitionFee.objects.create(degree_id=1, student_id=2, amount=250.00,
                                                      deadline=now.replace(year=now + 1))
            tuition_fees.append(tuition_fee_1)

            tuition_fee_2 = TuitionFee.objects.create(degree_id=1, student_id=2, amount=250.00,
                                                      deadline=now.replace(year=now + 2))
            tuition_fees.append(tuition_fee_2)

            tuition_fee_serializer = TuitionFeeSerializer(tuition_fees, many=True)
            return Response(tuition_fee_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TuitionFeePayView(APIView):
    def post(self, request, pk, format=None):
        try:
            tuition_fee = TuitionFee.objects.get(pk=pk)

            if tuition_fee.is_paid:
                return Response({
                    'status': '400',
                    'message': 'TuitionFee already paid.',
                }, status=status.HTTP_400_BAD_REQUEST)

            tuition_fee.is_paid = True
            tuition_fee.save()
            tuition_fee_serializer = TuitionFeeSerializer(tuition_fee)
            return Response(tuition_fee_serializer.data, status=status.HTTP_200_OK)

        except TuitionFee.DoesNotExist:
            raise Http404
