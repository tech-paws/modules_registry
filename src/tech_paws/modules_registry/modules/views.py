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

from tech_paws.modules_registry.modules.serializers import UpdateVersionSerializer, CreateVersionSerializer, ModuleLibSerializer
from tech_paws.modules_registry.modules.models import Module, ModuleVersion, ModuleLib


@api_view(["GET"])
def module_meta(request, module_id, version):
    with transaction.atomic():
        module = get_object_or_404(Module, id=module_id)
        module_version = get_object_or_404(ModuleVersion, module=module, version=version)
        module_libs = ModuleLib.objects.filter(uploaded=True, module_version=module_version)
        serializer = ModuleLibSerializer(module_libs, many=True)

        return Response({
            "repo": module_version.repository,
            "libs": serializer.data
        })


@api_view(["POST"])
def upload_lib(request, module_id, version, os, arch, lib):
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
def publis_version(request):
    serializer = CreateVersionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    id = serializer.validated_data["id"]
    version = serializer.validated_data["version"]

    with transaction.atomic():
        module, _ = Module.objects.get_or_create(id=id)

        ignore = {"id", "platforms"}
        fields = set(serializer.validated_data) - ignore

        module_version = ModuleVersion.objects.filter(version=version, module=module)

        if module_version.count() > 0:
            ModuleVersion.objects \
                .filter(version=version, module=module) \
                .update(**{key: serializer.validated_data[key] for key in fields})
            module_version = ModuleVersion.objects.get(version=version, module=module)
        else:
            module_version = ModuleVersion.objects.create(
                module=module,
                **{key: serializer.validated_data[key] for key in fields}
            )

        _create_platforms(module_version, serializer.validated_data["platforms"]);
        module_version.save()

    return Response({}, status=status.HTTP_200_OK)


def _create_platforms(module_version, platforms):
    for platform in platforms:
        if len(set(platform["libs"])) != len(platform["libs"]):
            duplicates = [item for item, count in collections.Counter(platform["libs"]).items() if count > 1]
            raise ValidationError(f"avoid libs duplications: {duplicates}")

        for lib in platform["libs"]:
            module_lib = ModuleLib.objects.filter(
                module_version=module_version,
                os=platform["os"],
                arch=platform["arch"],
                name=lib
            )

            if module_lib.count() == 0:
                ModuleLib.objects.create(
                    module_version=module_version,
                    os=platform["os"],
                    arch=platform["arch"],
                    name=lib
                )
