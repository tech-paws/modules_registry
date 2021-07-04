from django.contrib import admin
from tech_paws.modules_registry.modules.models import Module, ModuleVersion, ModuleLib


class LibAdmin(admin.ModelAdmin):
    list_display = ('module_version', 'name', 'os', 'arch', 'uploaded',)
    list_filter = ('uploaded', 'module_version', 'os', 'arch')


class VersionAdmin(admin.ModelAdmin):
    list_display = ('module', 'name', 'version',)
    list_filter = ('module__id',)


admin.site.register(Module)
admin.site.register(ModuleVersion, VersionAdmin)
admin.site.register(ModuleLib, LibAdmin)
