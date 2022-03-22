from rest_framework import serializers
from django.conf import settings
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import Distribution, Client, Message, Operator, Tag, StatusChoice


class StatusChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusChoice
        fields = ('OK', 'NO')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('tag',)


class OperatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Operator
        fields = ('operator_code',)


class MessageWithStatusSerializer(serializers.ModelSerializer):

    status = StatusChoiceSerializer(required=False)

    class Meta:
        model = Message
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        exclude = ('status', )


class DistributionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Distribution
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    tag = serializers.SlugRelatedField(slug_field='tag', many=True, queryset=Tag.objects.all(), required=False)
    time_zone = TimeZoneSerializerField(required=False)

    class Meta:
        model = Client
        exclude = ('operator',)

    def get_operator(self):
        phone_number = self.validated_data.get('phone_number')
        if phone_number:
            operator_code = int(self.validated_data.get('phone_number')[1:4])
            mobile_operator_code = Operator.objects.get_or_create(operator_code=operator_code)
            return mobile_operator_code

    def create(self, validated_data):

        tags = Tag.objects.filter(tag__in=validated_data.get('tag', []))

        client = Client.objects.create(
            phone_number=validated_data.get('phone_number'),
            operator_code=self.get_operator(),
            time_zone=validated_data.get('time_zone', settings.TIME_ZONE),
        )
        client.tag.set(tags)
        return client

    def update(self, client, validated_data):

        phone_number = validated_data.get('phone_number')
        if phone_number and (phone_number != client.phone_number):
            client.operator_code = self.get_operator()

        client.phone_number = validated_data.get('phone_number', client.phone_number)
        client.time_zone = validated_data.get('time_zone', client.time_zone)

        tags = Tag.objects.filter(tag__in=validated_data.get('tag', []))
        client.tag.set(tags)

        client.save()

        return client
