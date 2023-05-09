from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Mapped, declarative_base


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

    source: Mapped[String] = Column(String)
    sourceId: Mapped[Integer] = Column(Integer)

    def setProduct(self, v): self.product = v
    def setDate(self, v): self.date = v
    def setRegion(self, v): self.region = v
    def setQty(self, v): self.qty = v
    def setCost(self, v): self.cost = v
    def setAmt(self, v): self.amt = v
    def setTax(self, v): self.tax = v
    def setTotal(self, v): self.total = v

    def fromJson(self, json: dict):
        self.product = json["product"]
        self.source = json["source"]
        self.date = json["date"]
        self.region = json["region"]
        self.qty = json["qty"]
        self.cost = json["cost"]
        self.amt = json["amt"]
        self.tax = json["tax"]
        self.total = json["total"]
        self.sourceId = json["id"]


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
            str(self.source),
            str(self.id),
            str(self.sourceId)
        ]

    def __repr__(self) -> str:
        return f"""Product(\
sourceId={self.sourceId!r}, \
source={self.source!r}, \
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
