from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from tech_paws.modules_registry.modules.serializers import UpdateVersionSerializer, CreateVersionSerializer
from tech_paws.modules_registry.modules.models import Module, ModuleVersion


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

        print(dependencies)

        ignore = {"id", "dependencies"}
        fields = set(serializer.validated_data) - ignore
        module_version = ModuleVersion.objects.create(
            module = module,
            **{key: serializer.validated_data[key] for key in fields}
        )

        for dep in dependencies:
            module_version.dependencies.add(dep)

        module_version.save()

    return Response({}, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_version_meta(request):
    serializer = UpdateVersionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    id = serializer.validated_data["id"]
    module = get_object_or_404(Module, id=id)

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
