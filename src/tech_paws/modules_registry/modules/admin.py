from django.contrib import admin
from tech_paws.modules_registry.modules.models import Module, ModuleVersion, ModuleLib


class LibAdmin(admin.ModelAdmin):
    list_display = ('module_version', 'name', 'uploaded',)
    list_filter = ('uploaded', 'module_version',)


class VersionAdmin(admin.ModelAdmin):
    list_display = ('module', 'name', 'version', 'published',)
    list_filter = ('module__id', 'published',)


admin.site.register(Module)
admin.site.register(ModuleVersion, VersionAdmin)
admin.site.register(ModuleLib, LibAdmin)
