"""
Сервис работы с историей продаж.
Содержит функцию которая возвращает список продаж по конкретному партнёру для формирования отчётов и отображения в интерфейсе
"""

from sqlalchemy.orm import Session
from db.models import Sale, SaleItem, Product

def get_partner_sales(session: Session, partner_id: int):
    # Возвращает список продаж по партнёру в удобном виде.
    try:
        rows = (
            session.query(
                Sale.sale_date,
                Product.name,
                SaleItem.quantity,
            )
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .join(Product, Product.id == SaleItem.product_id)
            .filter(Sale.partner_id == partner_id)
            .order_by(Sale.sale_date.desc(), Product.name)
            .all()
        )
        return rows
    except Exception as e:
        print(f"Ошибка при получении истории продаж для партнёра id={partner_id}:", e)
        return []
