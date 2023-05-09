from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import Mapped, declarative_base, Session


Base = declarative_base()
class Product(Base):
    __tablename__ = "products"

    id: Mapped[Integer] = Column(Integer, primary_key=True, autoincrement="auto")
    product: Mapped[String] = Column(String(30))
    date: Mapped[String] = Column(String)
    region: Mapped[String] = Column(String(30))
    qty: Mapped[Integer] = Column(Integer, default=0)
    cost: Mapped[Float] = Column(Float, default=0)
    amt: Mapped[Float] = Column(Float, default=0)
    tax: Mapped[Float] = Column(Float, default=0)
    total: Mapped[Float] = Column(Float, default=0)

    created: Mapped[Boolean] = Column(Boolean, default=True)
    edited: Mapped[Boolean] = Column(Boolean, default=False)
    toDelete: Mapped[Boolean] = Column(Boolean, default=False)

    def setProduct(self, v):
        if not self.created:
            self.edited = True
        
        self.product = v
    
    def setDate(self, v):
        if not self.created:
            self.edited = True
        
        self.date = v

    def setRegion(self, v):
        if not self.created:
            self.edited = True
        
        self.region = v

    def setQty(self, v):
        if not self.created:
            self.edited = True
        
        self.qty = v

    def setCost(self, v):
        if not self.created:
            self.edited = True
        
        self.cost = v

    def setAmt(self, v):
        if not self.created:
            self.edited = True
        
        self.amt = v

    def setTax(self, v):
        if not self.created:
            self.edited = True
        
        self.tax = v

    def setTotal(self, v):
        if not self.created:
            self.edited = True
        
        self.total = v


    def softDelete(self, session: Session):
        if self.created:
            session.delete(self)
        else:
            self.toDelete = True
            session.add(self)
        session.commit()
        # softDelete
    
    def setSynced(self, session: Session):
        if self.toDelete:
            session.delete(self)
        else:
            self.created = False
            self.edited = False
            session.add(self)
        
        session.commit()
        # setSynced

    def toJson(self):
        return {
            "product": self.product,
            "date": self.date,
            "region": self.region,
            "qty": self.qty,
            "cost": self.cost,
            "amt": self.amt,
            "tax": self.tax,
            "total": self.total,
            "id": self.id,
        }

    def toList(self):
        return [
            str(self.product),
            str(self.date),
            str(self.region),
            str(self.qty),
            str(self.cost),
            str(self.amt),
            str(self.tax),
            str(self.total),
            str(self.id),
        ]

    def __repr__(self) -> str:
        return f"""Product(\
id={self.id!r}, \
product={self.product!r}, \
date={self.date!r} \
region={self.region!r}, \
qty={self.qty!r} \
cost={self.cost!r} \
amt={self.amt!r} \
tax={self.tax!r} \
total={self.total!r} \
)"""
