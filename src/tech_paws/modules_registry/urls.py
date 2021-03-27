from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tech_paws.modules_registry.modules import views as modules_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_version_meta', modules_views.create_version_meta, name='create_version_meta'),
    path('update_version_meta', modules_views.update_version_meta, name='update_version_meta'),
]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
