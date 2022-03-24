import json
from datetime import datetime, timezone

import requests.auth
from celery import shared_task
from django.db.models import Q

from core.models import Message, Distribution, Client
from security_code import token


def send_distribution(distribution):
    if distribution.message_set.exists():
        messages = distribution.message_set.all()
        for message in messages:
            send_message_for_client(message.client, distribution)
            clients = distribution.get_clients()
            for client in clients:
                set(client.message_set.all())
    else:
        tags = distribution.filter_tags.all()
        operators = distribution.filter_operators.all()
        clients = Client.objects.filter(Q(tag__in=tags) | Q(operator__in=operators))
        for client in clients:
            send_message_for_client(client, distribution)


def send_message_for_client(client, distribution):
    if Message.objects.filter(client=client, distribution=distribution).exists():
        message = Message.objects.get(client=client, distribution=distribution)
    else:
        message = Message.objects.create(client=client, distribution=distribution)
        print('Сообщение создано')
    message.save()
    data = json.dumps(
        {
            'id': message.id,
            'phone': int(client.phone_number),
            'text': distribution.text
        }
    )
    HEADERS = {
        'Authorization': 'Bearer ' + token,
        'content-type': 'application/json'
    }
    URL = 'https://probe.fbrq.cloud/v1/send/'
    try:
        response = requests.post(url=URL + f'{message.id}', data=data, headers=HEADERS, timeout=1)
        response.raise_for_status()
        if response.status_code == requests.codes.ok:
            message.status = 'отпралено'
    except Exception as error:
        print(error)


@shared_task
def send_complete_distribution():
    distributions = Distribution.objects.filter(stop_datetime__lte=datetime.now(tz=timezone.utc))
    for distribution in distributions:
        clients = distribution.get_clients()
        for client in clients:
            send_message_for_client(client, distribution)
    print('рассылки отправлены')

