from .RMQConsumer import RabbitMQConsumer


class RabbitMQConnection:
    def __init__(self, identifier):
        self.clientId = identifier
        self.consumer = RabbitMQConsumer()
        # __init__
    
    def connect(self):
        self.consumer.connect()
        # connect
    
    def disconnect(self):
        try: self.consumer.disconnect()
        except: pass
        # disconnect
    