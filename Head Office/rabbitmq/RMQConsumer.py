import pika
from pika.exceptions import NackError, UnroutableError
from Config import Config


class RabbitMQConsumer:
    def __init__(self):
        self.connected = False
        # __init__
    
    def connect(self):
        self.connection = pika.BlockingConnection(Config.RMQ_CONNECTION)
        self.channel = self.connection.channel()
        self.channel.confirm_delivery() # https://www.rabbitmq.com/confirms.html#publisher-confirms
        self.connected = True
        # connect

    def disconnect(self):
        self.channel.close()
        self.connection.close()
        self.connected = False
        # disconnect

    def declareDurableQueue(self, queue, **args):
        res = self.channel.queue_declare(queue=queue, durable=True, **args)
        return res.method.queue
        
    def declareExchange(self, exchange, exchType):
        return self.channel.exchange_declare(exchange=exchange, exchange_type=exchType)
    
    def bindQueueExch(self, queue, exchange):
        return self.channel.queue_bind(exchange=exchange, queue=queue)
    
    def sendMessage(self, message: str, queue="", exchange="") -> bool:
        try:
            self.channel.basic_publish(exchange=exchange,
                      routing_key=queue,
                      mandatory=True,
                      body=message)
            return True
        except: return False
    
    def readQueue(self, queue, **args):
        return self.channel.basic_get(queue, **args)

    def sendNack(self, tag):
        self.channel.basic_nack(tag)
    
    def sendAck(self, tag):
        self.channel.basic_ack(tag)
