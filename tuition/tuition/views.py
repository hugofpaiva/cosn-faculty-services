from django.http import Http404
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from rest_framework import generics, mixins, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from tuition.models import TuitionFee
from tuition.serializers import TuitionFeeSerializer, CreateTuitionFeeSerializer, ErrorSerializer


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
                'details': 'A student_id is needed to filter the TuitionFees',
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
    @extend_schema(
        request=CreateTuitionFeeSerializer,
        examples=[
            OpenApiExample(
                name="Create Monthly TuitionFees",
                description="Create Monthly TuitionFees",
                status_codes=[201],
                request_only=True,
                value=
                {
                    "degree_id": 1,
                    "student_id": 1,
                    "payment_type": "MONTHLY"
                }

            ),
            OpenApiExample(
                name="Create Annual TuitionFees",
                description="Create Annual TuitionFees",
                status_codes=[201],
                request_only=True,
                value=
                {
                    "degree_id": 1,
                    "student_id": 1,
                    "payment_type": "ANNUAL"
                }

            ),
            OpenApiExample(
                name="Created Monthly TuitionFees successfully",
                description="Created Monthly TuitionFees successfully",
                status_codes=[201],
                response_only=True,
                value=[{"id": 1,
                        "degree_id": 1,
                        "student_id": 1,
                        "amount": "250.00",
                        "deadline": "2022-01-11",
                        "is_paid": False} for i in range(0, 10)]

            ),
            OpenApiExample(
                name="Created Annual TuitionFees successfully",
                description="Created Annual TuitionFees successfully",
                status_codes=[201],
                response_only=True,
                value=[{"id": 1,
                        "degree_id": 1,
                        "student_id": 1,
                        "amount": "2500.00",
                        "deadline": "2022-01-11",
                        "is_paid": False}]

            )
        ],
        responses={201: TuitionFeeSerializer(),

                   })
    def post(self, request, format=None):
        serializer = CreateTuitionFeeSerializer(data=request.data)
        if serializer.is_valid():
            # TODO call other service & errors examples on OpenAPI
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

    @extend_schema(
        request=None,
        examples=[OpenApiExample(
            name="Paid Successfully",
            description="Paid with success",
            status_codes=[200],
            value=
            {
                "id": 1,
                "degree_id": 1,
                "student_id": 1,
                "amount": "250.00",
                "deadline": "2022-12-11",
                "is_paid": True
            },

        ), OpenApiExample(
            name="Not Found",
            status_codes=[404],
            description="TuitionFee not found",
            value=
            {'details': 'Not found'},

        ),
            OpenApiExample(
                name="Already Paid",
                status_codes=[400],
                description="Paid already paid",
                value=
                {'details': 'TuitionFee already paid.'},

            )
        ],
        responses={200: TuitionFeeSerializer,
                   404: ErrorSerializer, 400: ErrorSerializer})
    def post(self, request, pk, format=None):
        try:
            tuition_fee = TuitionFee.objects.get(pk=pk)

            if tuition_fee.is_paid:
                return Response({
                    'details': 'TuitionFee already paid.',
                }, status=status.HTTP_400_BAD_REQUEST)

            tuition_fee.is_paid = True
            tuition_fee.save()
            tuition_fee_serializer = TuitionFeeSerializer(tuition_fee)
            return Response(tuition_fee_serializer.data, status=status.HTTP_200_OK)

        except TuitionFee.DoesNotExist:
            raise Http404
