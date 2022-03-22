from enum import Enum
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from timezone_field import TimeZoneField


class Operator(models.Model):
    operator_code = models.PositiveSmallIntegerField(primary_key=True, verbose_name='мобильный оператор')

    def __str__(self):
        return f'{self.operator_code}'


class Tag(models.Model):
    tag = models.CharField(max_length=50, primary_key=True, verbose_name='тэг')

    def __str__(self):
        return self.tag


class StatusChoice(Enum):   # A subclass of Enum
    OK = "отправлено"
    NO = "не доставлен"


class Distribution(models.Model):
    start_datetime = models.DateTimeField(auto_now=True, verbose_name='дата и время запуска рассылки')
    text = models.TextField(verbose_name='текст сообщения для доставки клиенту')
    filter_operators = models.ManyToManyField(Operator, related_name='distribution', blank=True,
                                              verbose_name='фильтр операторов клиентов для рассылки')
    filter_tags = models.ManyToManyField(Tag, related_name='distribution', blank=True,
                                         verbose_name='фильтр тегов клиентов для рассылки')
    stop_datetime = models.DateTimeField(verbose_name='дата и время окончания рассылки')

    # фильтр клиентов по тэгу и мобильному оператору
    def get_clients(self):
        if len(self.filter_tags.all()):
            clients = Client.objects.filter(
                tag__in=self.filter_tags.all()
            )
        elif len(self.filter_operators.all()):
            clients = Client.objects.filter(
                operator__in=self.filter_operators.all()
            )
        else:
            clients = Client.objects.all()
        return clients

    # фильтр времени, чтобы не превышало время остановки рассылки
    def get_messages(self):
        messages = Message.objects.filter(
            create_datetime__lte=self.stop_datetime
        )
        return messages

    def __str__(self):
        return f'id: {self.pk}, дата и время запуска рассылки: {self.stop_datetime}, текст сообщения: {self.text}, ' \
               f'конец рассылки: {self.stop_datetime}\n фильтр тегов клиентов для рассылки: ' \
               f'{list(self.filter_tags.all())}\n, фильтр операторов клиентов для рассылки: ' \
               f'{list(self.filter_operators.all())}'


class Client(models.Model):
    # Валидатор номера телефона клиента, который проверяет на соответствие формату 7XXXXXXXXXX (где X от 0 до 9)
    phone_number_regex = RegexValidator(regex=r'^7\d{10}$')
    # Уникальный номер телефона, не превышающий длину в 11 символов
    phone_number = models.CharField(validators=[phone_number_regex], max_length=11, unique=True,
                                    verbose_name='номер телефона клиента')
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='clients',
                                 verbose_name='мобильный оператор')
    tag = models.ManyToManyField(Tag, related_name='clients', blank=True, verbose_name='тэг(произвольная метка)')
    time_zone = TimeZoneField(choices_display="WITH_GMT_OFFSET",
                              default=settings.TIME_ZONE, blank=True, verbose_name='часовой пояс')

    def __str__(self):
        return f'id: {self.pk}, phone: {self.phone_number}, оператор: {self.operator}, тег: {self.tag}, ' \
               f'часовой пояс: {self.time_zone}'


class Message(models.Model):
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    status = models.CharField(
        max_length=5,
        choices=[(tag, tag.value) for tag in StatusChoice], # Choices is a list of Tuple
        verbose_name='статус отправки'
    )
    distribution = models.ForeignKey(Distribution, verbose_name='id рассылки',
                                     on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, verbose_name='id клиента', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'id: {self.id}, Дата создания: {self.create_datetime}, id рассылки: {self.distribution.pk}, ' \
               f'id клиента: {self.client.pk}, статус: {self.status}'
