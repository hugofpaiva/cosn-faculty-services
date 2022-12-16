import io
import requests
from django.http import Http404, FileResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil.relativedelta import relativedelta
import datetime
from sentry_sdk import capture_exception
from reportlab.pdfgen import canvas
import decimal

from tuition.models import TuitionFee
from tuition.serializers import TuitionFeeSerializer, CreateTuitionFeeSerializer, ErrorSerializer, \
    ReceiptParametersSerializer

NUMBER_FAILURES = 10
end_of_timeout = None
failures_current_5_minutes = 0
last_date_changed = datetime.datetime.now()


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

    @extend_schema(
        parameters=[
            OpenApiParameter(name="student_id", required=True, type=int),
        ],
    )
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


def last_day_of_month(now):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = now.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)


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
                    "degree_id": 'd34897c6-0a8c-4d21-8ec7-f1ac6a771a4f',
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
                    "degree_id": 'd34897c6-0a8c-4d21-8ec7-f1ac6a771a4f',
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
                        "degree_id": 'd34897c6-0a8c-4d21-8ec7-f1ac6a771a4f',
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
                        "degree_id": 'd34897c6-0a8c-4d21-8ec7-f1ac6a771a4f',
                        "student_id": 1,
                        "amount": "2500.00",
                        "deadline": "2022-01-11",
                        "is_paid": False}]

            ),
            OpenApiExample(
                name="Tuition value of the degree is not available",
                description="Tuition value of the degree is not available",
                status_codes=[503],
                response_only=True,
                value={"details": "Tuition value of the degree is not available"}
            )
        ],
        responses={201: TuitionFeeSerializer,
                   503: ErrorSerializer
                   })
    def post(self, request, format=None):
        serializer = CreateTuitionFeeSerializer(data=request.data)
        if serializer.is_valid():
            global end_of_timeout
            if end_of_timeout:
                if datetime.datetime.now() < end_of_timeout:
                    return Response({'details': 'Tuition value of the degree is not available'},
                                    status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    end_of_timeout = None

            url = f"https://cosn-gateway.brenosalles.workers.dev/degrees/{serializer.validated_data.get('degree_id')}"
            response = None
            try:
                response = requests.get(url, timeout=3)
                response.raise_for_status()
            except Exception as e:
                capture_exception(e)

            if response and response.status_code == 200:
                data = response.json()
                if 'tuition' in data:
                    try:
                        value = decimal.Decimal(data['tuition'])
                        now = last_day_of_month(datetime.datetime.now().date())
                        tuition_fees = []
                        range_limit = 1

                        if serializer.validated_data.get('payment_type') == "MONTHLY":
                            range_limit = 10
                        
                        new_value = value / range_limit
                        
                        for i in range(range_limit):
                            new_deadline = now + relativedelta(months=+i)
                            new_deadline = last_day_of_month(new_deadline)
                            tuition_object = TuitionFee.objects.create(degree_id=serializer.validated_data.get('degree_id'),
                                                          student_id=serializer.validated_data.get(
                                                              'student_id'), amount=new_value,
                                                          deadline=new_deadline)
                            tuition_object.save()
                            tuition_fees.append(tuition_object)

                        tuition_fee_serializer = TuitionFeeSerializer(tuition_fees, many=True)
                        return Response(tuition_fee_serializer.data, status=status.HTTP_201_CREATED)
                    except ValueError as e:
                        capture_exception(e)
            elif response and response.status_code == 404:
                pass
            else:
                global last_date_changed
                global failures_current_5_minutes
                if (datetime.datetime.now() - last_date_changed).total_seconds() > 60 * 5:
                    failures_current_5_minutes = 1
                else:
                    failures_current_5_minutes += 1
                last_date_changed = datetime.datetime.now()

                if failures_current_5_minutes > NUMBER_FAILURES:
                    end_of_timeout = datetime.datetime.now() + datetime.timedelta(minutes=5)

            return Response({'details': 'Tuition value of the degree is not available'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
                "degree_id": 'd34897c6-0a8c-4d21-8ec7-f1ac6a771a4f',
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
                description="TuitionFee already paid",
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


class TuitionFeeReceiptCreateView(APIView):

    @extend_schema(request=None,
                   parameters=[
                       OpenApiParameter(name="tuition_fee_id", required=True, type=int),
                   ],

                   examples=[OpenApiExample(
                       name="TuitionFee not yet paid.",
                       status_codes=[400],
                       description="TuitionFee not yet paid.",
                       value=
                       {'details': 'TuitionFee not yet paid.'},

                   )],
                   responses={404: ErrorSerializer, 400: ErrorSerializer})
    def get(self, request, format=None):
        serializer = ReceiptParametersSerializer(data=request.query_params)
        if serializer.is_valid():
            try:
                tuition_fee = TuitionFee.objects.all().get(pk=serializer.validated_data.get('tuition_fee_id'))
                if not tuition_fee.is_paid:
                    return Response({
                        'details': 'TuitionFee not yet paid.',
                    }, status=status.HTTP_400_BAD_REQUEST)

                buffer = io.BytesIO()

                pdf = canvas.Canvas(buffer)

                pdf.setTitle("Receipt")
                pdf.drawString(200, 500, f"This is the excellent receipt of Tuition nº {tuition_fee.id}")
                pdf.drawString(200, 480, f"Student id: {tuition_fee.student_id}")
                pdf.drawString(200, 460, f"Amount: {tuition_fee.amount}")
                pdf.drawString(200, 440, f"Deadline: {tuition_fee.deadline}")
                pdf.showPage()
                pdf.save()

                buffer.seek(0)
                return FileResponse(buffer, as_attachment=True, filename="certificate.pdf")
            except TuitionFee.DoesNotExist:
                raise Http404

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
