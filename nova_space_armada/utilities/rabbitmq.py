import os
import pika
import json
import base64
import requests
from nova_space_armada import config


def host(q_name, callback):
    rabbit_host = config.rabbit_host
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, socket_timeout=10))
    channel = connection.channel()
    channel.queue_declare(queue=q_name, durable=True)

    channel.basic_consume(queue=q_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    return connection


def client(q_name, username, password,  body=b''):
    """
    :param q_name:
    :param username:
    :param password:
    :param body: json.dumps([{}]).encode
    :return:
    """
    client_host = config.rabbit_host
    credentials = pika.PlainCredentials(username, password)
    with pika.BlockingConnection(pika.ConnectionParameters(host=client_host, credentials=credentials)) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=q_name, durable=True)
        channel.basic_publish(exchange='', routing_key=q_name, body=body)


def http_request(q_name, username, password, body: str):
    """
    :param q_name:
    :param username:
    :param password:
    :param body: json.dumps([{}]) without .encode
    :return:
    """
    client_host = config.rabbit_host
    authorization = f'{username}:{password}'.encode()
    basic_auth = base64.urlsafe_b64encode(authorization).decode()

    data = {"properties": {"content-type": "application/json", 'authorization': f'Basic {basic_auth}'}, "routing_key": q_name, "payload": body, "payload_encoding": "string"}
    data = json.dumps(data).encode()

    ses = requests.session()
    ses.headers.update({'Authorization': f'Basic {basic_auth}',
                        'Content-Type': 'application/json'})

    ses.post(f'http://{client_host}:15672/api/exchanges/%2F/amq.default/publish', data)
