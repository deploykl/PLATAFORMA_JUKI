from rest_framework import serializers
from .models import Ipress, CategoriaPregunta, Pregunta, Respuesta

class CategoriaPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPregunta
        fields = '__all__'

class PreguntaSerializer(serializers.ModelSerializer):
    categoria = CategoriaPreguntaSerializer(read_only=True)
    
    class Meta:
        model = Pregunta
        fields = '__all__'

class IpressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ipress
        fields = '__all__'

class RespuestaSerializer(serializers.ModelSerializer):
    pregunta = serializers.PrimaryKeyRelatedField(queryset=Pregunta.objects.all())
    ipress = serializers.PrimaryKeyRelatedField(queryset=Ipress.objects.all())
    
    class Meta:
        model = Respuesta
        fields = '__all__'
        extra_kwargs = {
            'observaciones': {'allow_null': True, 'required': False},
            'riesgos_problemas': {'allow_null': True, 'required': False},
            'responsable': {'allow_null': True, 'required': False},
            'monitor': {'allow_null': True, 'required': False}
        }
