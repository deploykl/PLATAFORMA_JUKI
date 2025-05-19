from django.db import models
from django.contrib.auth.models import User
    
class Ipress(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre del registro")
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código único")
    categoria = models.CharField(max_length=100, verbose_name="Categoría")
    departamento = models.CharField(max_length=50, verbose_name="Departamento")
    provincia = models.CharField(max_length=50, verbose_name="Provincia")
    disa = models.CharField(max_length=50, verbose_name="DISA")
    distrito = models.CharField(max_length=50, verbose_name="Distrito")
    
    class Meta:
        verbose_name = "Ipress"
        verbose_name_plural = "Ipresses"
    
    def __str__(self):
        return f"{self.nombre} - {self.codigo}"

class CategoriaPregunta(models.Model):
    descripcion = models.CharField(max_length=255, verbose_name="Descripción", unique=True)

    def __str__(self):
        return f"Detalle : {self.descripcion}"
 
class Pregunta(models.Model):
    descripcion = models.TextField(verbose_name="Texto de la pregunta")
    categoria = models.ForeignKey(CategoriaPregunta, on_delete=models.SET_NULL, null=True, verbose_name="Categoría")
    
    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"

    def __str__(self):
        return f"Pregunta {self.descripcion}: {self.categoria}..."



        
class Respuesta(models.Model):
    OPCIONES_CUMPLIMIENTO = [
        ('SI', 'Sí'),
        ('NO', 'No'),
        ('NA', 'No aplica'),
    ] 
      
    ipress = models.ForeignKey(Ipress, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    cumplimiento = models.CharField(max_length=2, choices=OPCIONES_CUMPLIMIENTO, verbose_name="Cumple")
    puntaje = models.PositiveIntegerField(default=0, verbose_name="Puntaje")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    riesgos_problemas = models.TextField(blank=True, null=True, verbose_name="Riesgos/Problemas")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    responsable = models.CharField(max_length=100, verbose_name="Responsable de la Ipress", blank=True, null=True)
    monitor = models.CharField(max_length=100, verbose_name="Monitor", blank=True, null=True)
        
    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
    
    def __str__(self):
        return f"Respuesta a {self.cumplimiento}"

    def save(self, *args, **kwargs):
        # Auto-calcula el puntaje al guardar
        self.puntaje = {
            'SI': 1,
            'NO': 0,
            'NA': 0.5
        }.get(self.cumplimiento, 0)
        super().save(*args, **kwargs)