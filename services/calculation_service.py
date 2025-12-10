# Сервис для работы с расчётом количества материала

from math import ceil
from sqlalchemy.orm import Session
from db.models import ProductType, MaterialType

def get_product_types(session: Session) -> list[ProductType]:
    """
    Возвращает список типов продукции, отсортированных по имени
    Используется в диалоге расчёта материала для заполнения выпадающего списка
    """
    try:
        return session.query(ProductType).order_by(ProductType.name).all()
    except Exception as e:
        # В случае ошибки возвращаем пустой список
        print("Ошибка при загрузке типов продукции:", e)
        return []


def get_material_types(session: Session) -> list[MaterialType]:
    """
    Возвращает список типов материалов, отсортированных по имени
    Используется в диалоге расчёта материала для заполнения списка типов материала
    """
    try:
        return session.query(MaterialType).order_by(MaterialType.name).all()
    except Exception as e:
        print("Ошибка при загрузке типов материала:", e)
        return []

def calculate_required_material(session: Session, product_type_id: int, material_type_id: int, quantity: int, param1: float, param2: float,) -> int:
    """
    Расчёт количества материала, требуемого для производства продукции
    Параметры:
        product_type_id  - идентификатор типа продукции
        material_type_id - идентификатор типа материала
        quantity         - количество единиц продукции (целое > 0)
        param1, param2   - параметры продукции (вещественные > 0)
    Формула:
        base = quantity * param1 * param2 * type_coefficient
        total = base * (1 + defect_percent / 100)
    Возвращает:
        целое количество материала c округлением вверх , либо -1
    """
    try:
        quantity = int(quantity)
        param1 = float(param1)
        param2 = float(param2)
    except (TypeError, ValueError):
        return -1

    if quantity <= 0 or param1 <= 0 or param2 <= 0:
        # Логически некорректные значения
        return -1

    # Пытаемся получить записи из БД
    try:
        product_type = session.get(ProductType, product_type_id)
        material_type = session.get(MaterialType, material_type_id)
    except Exception as e:
        print("Ошибка при получении данных для расчёта материала:", e)
        return -1

    # Если один из типов не найден — считаем, что расчёт невозможен.
    if product_type is None or material_type is None:
        return -1

    # Берём коэффициент и процент брака из БД 
    if product_type.type_coefficient is None or material_type.defect_percent is None:
        return -1
    try:
        type_coeff = float(product_type.type_coefficient)
        defect_percent = float(material_type.defect_percent)
    except (TypeError, ValueError):
        return -1

    # Базовый расход без учёта брака
    base_amount = quantity * param1 * param2 * type_coeff
    if base_amount <= 0:
        return -1

    # Учёт брака
    total_amount = base_amount * (1.0 + defect_percent / 100.0)
    if total_amount <= 0:
        return -1

    # Округляем вверх до целого количества материала использую ceil
    try:
        return int(ceil(total_amount))
    except Exception as e:
        print("Ошибка при округлении результата расчёта материала:", e)
        return -1
