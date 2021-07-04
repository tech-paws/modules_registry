from django.db import models

class Module(models.Model):
    class Meta:
        ordering = ["-last_modified_datetime"]

    id = models.CharField(max_length=60, unique=True, primary_key=True)
    create_datetime = models.DateTimeField(auto_now_add=True)
    last_modified_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id


class ModuleVersion(models.Model):
    class Meta:
        ordering = ["-create_datetime"]
        unique_together = ['module', 'version']

    module = models.ForeignKey(Module, related_name="module", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=40)
    create_datetime = models.DateTimeField(auto_now_add=True)
    homepage = models.URLField(blank=True, null=True)
    repository = models.URLField(blank=True, null=True)
    documentation = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.module.id} - {self.name} - {self.version}"


class ModuleLib(models.Model):
    class Meta:
        unique_together = ["module_version", "name", "os", "arch"]

    module_version = models.ForeignKey(ModuleVersion, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    os = models.CharField(max_length=255, default="linux")
    arch = models.CharField(max_length=40, default="x86_64")
    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.os} ({self.arch}) - {self.name} ({self.module_version.module.id} - {self.module_version.version})"
