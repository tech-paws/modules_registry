from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tech_paws.modules_registry.modules import views as modules_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('publish', modules_views.publis_version),
    path('upload/<module_id>/<version>/<os>/<arch>/<lib>', modules_views.upload_lib),
    path('meta/<module_id>/<version>', modules_views.module_meta),
]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
