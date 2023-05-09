from .RMQPublisher import RabbitMQPublisher


class RabbitMQConnection:
    def __init__(self, identifier):
        self.clientId = identifier
        self.publisher = RabbitMQPublisher()
        # __init__
    
    def connect(self):
        self.publisher.connect()
        # connect
    
    def disconnect(self):
        try: self.publisher.disconnect()
        except: pass
        # disconnect
    