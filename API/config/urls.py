from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import RedirectView  # <-- Importa esto

urlpatterns = [
    path('', RedirectView.as_view(url='/api/schema/swagger/', permanent=False)),  # <-- Redirección
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
