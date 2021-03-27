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
    dependencies = models.ManyToManyField("ModuleVersion", blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=40)
    create_datetime = models.DateTimeField(auto_now_add=True)
    homepage = models.URLField(blank=True)
    repository = models.URLField(blank=True)
    documentation = models.URLField(blank=True)

    def __str__(self):
        return f"{self.module.id} - {self.name} - {self.version}"
