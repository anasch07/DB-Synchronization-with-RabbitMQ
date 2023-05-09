import pika


class Config:
    RMQ_CONNECTION = pika.ConnectionParameters("4.tcp.eu.ngrok.io", port=14697)

