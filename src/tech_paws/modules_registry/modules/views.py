import collections
from pathlib import Path

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser

from tech_paws.modules_registry.modules.serializers import UpdateVersionSerializer, CreateVersionSerializer
from tech_paws.modules_registry.modules.models import Module, ModuleVersion, ModuleLib


@api_view(["POST"])
def update_lib(request, module_id, version, os, arch, lib):
    with transaction.atomic():
        module = get_object_or_404(Module, id=module_id)
        module_version = get_object_or_404(ModuleVersion, module=module, version=version)
        module_lib = get_object_or_404(ModuleLib, module_version=module_version, os=os, arch=arch, name=lib)

        if "file" not in request.FILES:
            raise ValidationError(f"file is not presented (use file field)")

        relative_root_dir = Path(module_id) / version / os / arch
        root_dir = settings.MODULES_ROOT / relative_root_dir
        Path(root_dir).mkdir(parents=True, exist_ok=True)

        with open(root_dir / lib, "wb") as dst:
            for chunk in request.FILES["file"].chunks():
                dst.write(chunk)

        module_lib.uploaded = True
        module_lib.save()

    return Response(
        {"uploaded_path": str(relative_root_dir)},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def publish_version(request, module_id, version):
    with transaction.atomic():
        module = get_object_or_404(Module, id=module_id)
        module_version = get_object_or_404(ModuleVersion, module=module, version=version)
        module_libs = ModuleLib.objects.filter(module_version=module_version)

        for lib in module_libs:
            if not lib.uploaded:
                raise ValidationError(f"version can't be published, because {lib.os}/{lib.arch}/{lib.name} didn't uploaded")

        module_version.published = True
        module_version.save()

    return Response({}, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_version_meta(request):
    serializer = CreateVersionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    id = serializer.validated_data["id"]
    version = serializer.validated_data["version"]

    with transaction.atomic():
        module, _ = Module.objects.get_or_create(id=id)
        module_version = ModuleVersion.objects.filter(version=version, module=module)

        if module_version.count() > 0:
            raise ValidationError(f"module version == {version} already exists")

        if "dependencies" in serializer.validated_data:
            dependencies = _resolve_dependencies(module, serializer.validated_data["dependencies"])
        else:
            dependencies = []

        ignore = {"id", "dependencies", "platforms"}
        fields = set(serializer.validated_data) - ignore

        module_version = ModuleVersion.objects.create(
            module=module,
            **{key: serializer.validated_data[key] for key in fields}
        )

        for dep in dependencies:
            module_version.dependencies.add(dep)

        _create_platforms(module_version, serializer.validated_data["platforms"]);
        module_version.save()

    return Response({}, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_version_meta(request):
    serializer = UpdateVersionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    id = serializer.validated_data["id"]
    version = serializer.validated_data["version"]

    with transaction.atomic():
        module = Module.objects.filter(id=id)

        if module.count() == 0:
            raise ValidationError(f"module with id = {id} couldn't find")

        module = module.first()
        module_version = ModuleVersion.objects.filter(version=version, module=module)

        if module_version.count() == 0:
            raise ValidationError(f"module with version == {version} couldn't find")

        if "dependencies" in serializer.validated_data:
            dependencies = _resolve_dependencies(module, serializer.validated_data["dependencies"])
        else:
            dependencies = []

        ignore = {"id", "dependencies"}
        fields = set(serializer.validated_data) - ignore
        ModuleVersion.objects \
            .filter(version=version, module=module) \
            .update(**{key: serializer.validated_data[key] for key in fields})

        module_version = ModuleVersion.objects.get(version=version, module=module)
        module_version.dependencies.clear()

        for dep in dependencies:
            module_version.dependencies.add(dep)

        module_version.save()

    return Response({}, status=status.HTTP_200_OK)



def _resolve_dependencies(module, dependencies):
    result = []

    for dep_str in dependencies:
        dep = dep_str.split("==")

        if len(dep) != 2:
            raise ValidationError(f"invalid dependency format: {dep_str}")

        id, version = dep

        module_version = ModuleVersion.objects.filter(version=version, module__id=id)

        if module_version.count() == 0:
            raise ValidationError(f"dependency {dep_str} couldn't find")

        if module_version.first().module.id == module.id:
            raise ValidationError(f"can't depend on youself")

        result.append(module_version.first())

    return result


def _create_platforms(module_version, platforms):
    for platform in platforms:
        if len(set(platform["libs"])) != len(platform["libs"]):
            duplicates = [item for item, count in collections.Counter(platform["libs"]).items() if count > 1]
            raise ValidationError(f"avoid libs duplications: {duplicates}")

        for lib in platform["libs"]:
            ModuleLib.objects.create(
                module_version=module_version,
                os=platform["os"],
                arch=platform["arch"],
                name=lib
            )
