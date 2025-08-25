from django.contrib.auth import get_user_model, authenticate
from django.db.models.functions import TruncDate
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

from .models import (FleetVehicle, PerformanceStat, Report, TrailDataPoint,
                     TrailVehicle, VehicleChartData, VehicleSummary,
                     VehicleType)
from .serializers import (RegisterSerializer, ReportSerializer,
                          TrailVehicleSerializer, UserSerializer,
                          VehicleChartDataSerializer, FleetVehicleSerializer,
                          VehicleSummarySerializer, VehicleTypeSerializer)

User = get_user_model()

class LoginAPI(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            return Response({'error': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPI(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class UserProfileAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

class UserListAPI(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class DashboardStatsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        fleet_vehicles = FleetVehicle.objects.all()
        performance_stats_qs = PerformanceStat.objects.values('key', 'value')
        return Response({
            'fleet_stats': FleetVehicleSerializer(fleet_vehicles, many=True).data,
            'performance_stats': {stat['key']: stat['value'] for stat in performance_stats_qs}
        })

class VehicleSelectionAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VehicleSummarySerializer
    queryset = VehicleSummary.objects.prefetch_related('vehicles').all()
    def get_object(self):
        fleet_type_query = self.request.query_params.get('fleet_type')
        if fleet_type_query:
            return generics.get_object_or_404(self.get_queryset(), fleet_type=fleet_type_query)
        return self.get_queryset().first()
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
             return Response({"error": "No vehicle summary data found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class VehicleAnalysisAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if 'fetch_filters' in request.query_params or not request.query_params:
            vehicle_types = VehicleType.objects.prefetch_related('registrations__chart_data').all()
            return Response({"filters": VehicleTypeSerializer(vehicle_types, many=True).data})
        reg_id = request.query_params.get('registration_id')
        date = request.query_params.get('date')
        if not reg_id or not date:
            return Response({'error': 'registration_id and date parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        chart_data = generics.get_object_or_404(VehicleChartData, registration_id=reg_id, date=date)
        return Response({"charts": VehicleChartDataSerializer(chart_data).data})

class TrailsAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if 'fetch_filters' in request.query_params or not request.query_params:
            trail_vehicles = TrailVehicle.objects.prefetch_related('trail_data').all()
            return Response({"filters": TrailVehicleSerializer(trail_vehicles, many=True).data})
        vehicle_id = request.query_params.get('vehicle_id')
        date = request.query_params.get('date')
        if not vehicle_id or not date:
            return Response({'error': 'vehicle_id and date parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)
        trail_points = TrailDataPoint.objects.filter(vehicle_id=vehicle_id, date=date)
        first_point = trail_points.first()
        if not first_point:
            return Response({"error": "No trail data found for the specified vehicle and date."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "metrics": first_point.metrics,
            "ecu_data": first_point.ecu_data,
            "trail_path": [p.coordinates for p in trail_points]
        })

class ReportsAPI(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer
    
    # --- PAGINATION CONFIGURATION ADDED HERE ---
    pagination_class = PageNumberPagination
    # Set a default page size
    pagination_class.page_size = 10 
    # Allow the frontend to override the page size with a 'page_size' query param
    pagination_class.page_size_query_param = 'page_size'

    def get_queryset(self):
        queryset = Report.objects.select_related('registration__vehicle_type').all().order_by('-name')
        
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(name__date__range=[start_date, end_date])
            except (ValueError, TypeError):
                pass
        
        if report_type := self.request.query_params.get('report_type'):
            queryset = queryset.filter(report_type=report_type)
        if vehicle_type := self.request.query_params.get('vehicle_type'):
            queryset = queryset.filter(registration__vehicle_type__name=vehicle_type)
        if reg_no := self.request.query_params.get('registration_no'):
            queryset = queryset.filter(registration__registration_number=reg_no)
            
        return queryset

    def get(self, request, *args, **kwargs):
        if 'fetch_filters' in request.query_params:
            return self._get_filter_options()
        return self.list(request, *args, **kwargs)

    def _get_filter_options(self):
        filters = {
            "reportTypes": Report.objects.values_list('report_type', flat=True).distinct(),
            "vehicleTypes": VehicleType.objects.values_list('name', flat=True).distinct(),
            "registrations": {
                vt.name: list(vt.registrations.values_list('registration_number', flat=True)) 
                for vt in VehicleType.objects.prefetch_related('registrations').all()
            },
            "dates": Report.objects.annotate(date_only=TruncDate('name'))
                                .values_list('date_only', flat=True).distinct().order_by('-date_only'),
        }
        return Response(filters)
class HealthCheckAPI(APIView):
    """
    A simple endpoint that returns a 200 OK status if the API is running.
    """
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)    