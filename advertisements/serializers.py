from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )
        read_only_fields = ['creator', ]

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`

        validated_data["creator"] = self.context["request"].user
        count_open = Advertisement.objects.filter(creator=validated_data["creator"], status='OPEN').count()

        if count_open >= 10:
            raise ValidationError({'detail': f'Ограничение, 10 объявлений максимум. У Вас открыто {count_open}.'})

        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # TODO: добавьте требуемую валидацию

        creator = self.context["request"].user
        count_open = Advertisement.objects.filter(creator=creator, status='OPEN').count()

        if data.get('status', ) == 'OPEN':
            if count_open >= 10:
                raise ValidationError({'detail': f'Ограничение, 10 объявлений максимум. У Вас открыто {count_open}.'})

        return data