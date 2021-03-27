from django.contrib import admin
from tech_paws.modules_registry.modules.models import Module, ModuleVersion

admin.site.register(Module)
admin.site.register(ModuleVersion)
