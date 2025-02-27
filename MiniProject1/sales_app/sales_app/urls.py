from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sales and Trading API",
        default_version="1.0.0",
        description="API for managing sales and trading of products",
    ),
    public=True,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('users.urls')),
    path('api/', include('products.urls')),
    path('api/', include('sales.urls')),
    path('api/', include('trading.urls')),

    path('api/swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
