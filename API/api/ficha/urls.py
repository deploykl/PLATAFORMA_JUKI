from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IpressViewSet,
    CategoriaPreguntaViewSet,
    PreguntaViewSet,
    RespuestaViewSet,
    SusaludProxyViewSet
)

router = DefaultRouter()

# Registra cada ViewSet con un prefijo diferente
router.register(r'ipress', IpressViewSet, basename='ipress')
router.register(r'categorias-pregunta', CategoriaPreguntaViewSet, basename='categorias-pregunta')
router.register(r'preguntas', PreguntaViewSet, basename='preguntas')
router.register(r'respuestas', RespuestaViewSet, basename='respuestas')
router.register(r'susalud-proxy', SusaludProxyViewSet, basename='susalud-proxy')  # Nueva ruta

urlpatterns = [
    path('', include(router.urls)),
]