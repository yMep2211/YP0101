# Модуль с ORM-моделями

'''
Здесь описана структура всех таблиц схемы partner_module
- типы партнёров и сами партнёры, контактные данные партнёров
- типы продукции и сами товары
- типы материала (для метода расчёта количества материала)
- продажи и строки продаж
- агрегированная таблица с суммарным количеством реализованной продукции по партнёру.
'''

from sqlalchemy import Column, Integer, BigInteger, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class PartnerType(Base):
    __tablename__ = "partner_types"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    partners = relationship("Partner", back_populates="partner_type")


class Partner(Base):
    __tablename__ = "partners"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    partner_type_id = Column(BigInteger, ForeignKey("partner_module.partner_types.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(255), nullable=False)
    director_full_name = Column(String(255), nullable=False)
    legal_address = Column(String(500), nullable=False)
    inn = Column(String(12), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)

    partner_type = relationship("PartnerType", back_populates="partners")
    contacts = relationship("PartnerContact", back_populates="partner", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="partner")
    summary = relationship("PartnerSalesSummary", back_populates="partner", uselist=False, cascade="all, delete-orphan")


class PartnerContact(Base):
    __tablename__ = "partner_contacts"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    partner_id = Column(BigInteger, ForeignKey("partner_module.partners.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)

    partner = relationship("Partner", back_populates="contacts")


class ProductType(Base):
    __tablename__ = "product_types"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    type_coefficient = Column(Numeric(10, 4), nullable=False)

    products = relationship("Product", back_populates="product_type")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_type_id = Column(BigInteger, ForeignKey("partner_module.product_types.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(255), nullable=False)
    article = Column(String(50), nullable=False, unique=True)
    min_price_for_partner = Column(Numeric(12, 2), nullable=False)

    product_type = relationship("ProductType", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")


class MaterialType(Base):
    __tablename__ = "material_types"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    defect_percent = Column(Numeric(6, 4), nullable=False)


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    partner_id = Column(BigInteger, ForeignKey("partner_module.partners.id", ondelete="RESTRICT"), nullable=False)
    sale_date = Column(Date, nullable=False)

    partner = relationship("Partner", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = {"schema": "partner_module"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sale_id = Column(BigInteger, ForeignKey("partner_module.sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("partner_module.products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class PartnerSalesSummary(Base):
    __tablename__ = "partner_sales_summary"
    __table_args__ = {"schema": "partner_module"}

    partner_id = Column(BigInteger, ForeignKey("partner_module.partners.id", ondelete="CASCADE"), primary_key=True)
    total_quantity = Column(BigInteger, nullable=False)

    partner = relationship("Partner", back_populates="summary")
