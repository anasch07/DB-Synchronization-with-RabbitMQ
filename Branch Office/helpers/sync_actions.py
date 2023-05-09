from models import Product
import json


def updateAction(product: Product) -> dict:
    prodJson = product.toJson()
    return {"action": "update", "product": prodJson}

def createAction(product: Product) -> dict:
    prodJson = product.toJson()
    return {"action": "create", "product": prodJson}

def deleteAction(product: Product) -> dict:
    prodJson = product.toJson()
    return {"action": "delete", "product": prodJson}

def genActionMessage(product: Product) -> str:
    """
        Order is important.
        If we edit a newly created product, we can send a createAction with new values directly.
    """
    toSend = {}
    if product.edited:
        toSend = updateAction(product)
    if product.created:
        toSend = createAction(product)
    if product.toDelete:
        toSend = deleteAction(product)
    return json.dumps(toSend)
