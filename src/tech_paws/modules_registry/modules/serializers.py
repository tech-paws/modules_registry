from rest_framework import serializers


class StringListField(serializers.ListField):
    child = serializers.CharField()


class UpdateVersionSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=60)
    dependencies = StringListField(allow_null=True, required=False)
    name = serializers.CharField(max_length=100, allow_null=True, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    version = serializers.CharField()
    homepage = serializers.URLField(allow_null=True, required=False)
    repository = serializers.URLField(allow_null=True, required=False)
    documentation = serializers.URLField(allow_null=True, required=False)


class CreateVersionSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=60)
    dependencies = StringListField(allow_null=True, required=False)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    version = serializers.CharField()
    homepage = serializers.URLField(allow_null=True, required=False)
    repository = serializers.URLField(allow_null=True, required=False)
    documentation = serializers.URLField(allow_null=True, required=False)
