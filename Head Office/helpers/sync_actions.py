from models import Product
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json


def handleCreateAction(product: dict, session: Session):
    prod = session.query(Product)\
        .filter(and_(Product.source == product['source'], Product.sourceId == product['id']))\
        .first()
    
    if prod is not None:
        return
    
    prod: Product = Product()
    prod.fromJson(product)
    session.add(prod)
    session.commit()
    # handleCreateAction


def handleUpdateAction(product: dict, session: Session):
    prod = session.query(Product)\
        .filter(and_(Product.source == product['source'], Product.sourceId == product['id']))\
        .first()
    
    if prod is None:
        raise "Product not found"

    prod.fromJson(product)
    session.add(prod)
    session.commit()
    # handleUpdateAction


def handleDeleteAction(product: dict, session: Session):
    prod = session.query(Product)\
        .filter(and_(Product.source == product['source'], Product.sourceId == product['id']))\
        .first()
    
    if prod is None:
        raise "Product not found"

    session.delete(prod)
    session.commit()
    # handleDeleteAction


def handleSyncAction(body: str, source: str, session: Session):
    data: dict = json.loads(body)
    if data.get('action') is None or data.get('product') is None:
        return
    data['product']['source'] = source
    if data['action'] == 'create':
        handleCreateAction(data['product'], session)

    elif data['action'] == 'update':
        handleUpdateAction(data['product'], session)

    elif data['action'] == 'delete':
        handleDeleteAction(data['product'], session)
    
    # handleSyncAction
