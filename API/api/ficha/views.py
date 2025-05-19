from django.shortcuts import render
from rest_framework.permissions import AllowAny
from .serializers import (
    IpressSerializer,
    CategoriaPreguntaSerializer,
    PreguntaSerializer,
    RespuestaSerializer
)
from api.ficha.models import *
from django_filters.rest_framework import DjangoFilterBackend  
from rest_framework.filters import OrderingFilter, SearchFilter
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, mixins

# Create your views here.
class IpressViewSet(viewsets.ModelViewSet):
    queryset = Ipress.objects.all()
    serializer_class = IpressSerializer
    permission_classes = [AllowAny]
    ordering = ["id"]
    ordering_fields = "__all__"
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    
class CategoriaPreguntaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaPregunta.objects.all()
    serializer_class = CategoriaPreguntaSerializer
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = '__all__'

class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = '__all__'


class RespuestaViewSet(viewsets.ModelViewSet):
    queryset = Respuesta.objects.all().select_related('ipress', 'pregunta')
    serializer_class = RespuestaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ipress', 'pregunta', 'cumplimiento']

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': str(e),
                'detail': 'Error al guardar la respuesta. Verifica los datos.'
            }, status=400)
 
 


# Nuevo ViewSet para el proxy de SUSALUD
class SusaludProxyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['q']  # Campo para la búsqueda

    def list(self, request, *args, **kwargs):
        search_term = request.query_params.get('q', '')
        
        try:
            response = requests.get(
                'http://datos.susalud.gob.pe/api/action/datastore/search.json',
                params={
                    'resource_id': '8bb014bd-bb39-40d8-bfd7-0c8bcb4eb37d',
                    'q': search_term,
                    'limit': 10
                },
                timeout=5
            )
            response.raise_for_status()
            return Response(response.json())
        except requests.RequestException as e:
            return Response({'error': str(e)}, status=500)
    