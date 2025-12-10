"""
Сервисные функции для работы с партнёрами
Содержит:
    загрузку типов партнёров и списка партнёров
    валидацию данных, введённых пользователем в диалоге
    создание и обновление партнёров и их контактов
    удаление партнёров
"""
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Partner, PartnerType, PartnerContact

def get_partner_types(session: Session) -> list[PartnerType]:
    # Получить список типов партнёров из базы данных
    try:
        return session.query(PartnerType).order_by(PartnerType.name).all()
    except Exception as e:
        print("Ошибка при загрузке типов партнёров:", e)
        return []

def get_all_partners(session: Session) -> list[Partner]:
    # Получить всех партнёров
    try:
        return session.query(Partner).order_by(Partner.name).all()
    except Exception as e:
        print("Ошибка при загрузке списка партнёров:", e)
        return []

def validate_partner_data(data: dict) -> None:
    """
    Проверка корректности данных по партнёру
    Проверяются:
        наименование партнёра
        ФИО директора
        юридический адрес
        ИНН (10 или 12 цифр, допускаем ввод с пробелами и символами, но проверяем только цифры)
        формат электронной почты *@*.*
        телефон (строка вида "+7 XXXXXXXXXX", т.е. ровно 10 цифр после +7)
        рейтинг (в диапазоне от 0 до 10)
    """
    errors: list[str] = []

    name = (data.get("name") or "").strip()
    director = (data.get("director_full_name") or "").strip()
    legal_address = (data.get("legal_address") or "").strip()
    inn = (data.get("inn") or "").strip()
    email = (data.get("email") or "").strip()
    phone_raw = (data.get("phone") or "").strip()
    rating = data.get("rating")

    if not name:
        errors.append("Наименование партнёра не заполнено.")
    if not director:
        errors.append("ФИО директора не заполнено.")
    if not legal_address:
        errors.append("Юридический адрес не заполнен.")

    if not inn:
        errors.append("ИНН не заполнен.")
    else:
        digits_inn = "".join(ch for ch in inn if ch.isdigit())
        if len(digits_inn) not in (10, 12):
            errors.append("ИНН должен содержать 10 или 12 цифр.")

    if email:
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_pattern, email):
            errors.append("Электронная почта указана некорректно (формат: имя@домен.зона).")

    if not phone_raw:
        errors.append("Телефон не заполнен.")
    else:
        if not phone_raw.startswith("+7"):
            errors.append("Телефон должен начинаться с +7.")
        digits_phone = "".join(ch for ch in phone_raw if ch.isdigit())
        if len(digits_phone) != 11 or not digits_phone.startswith("7"):
            errors.append("Телефон должен содержать ровно 10 цифр после +7.")

    if rating is None or not (0 <= rating <= 10):
        errors.append("Рейтинг должен быть в диапазоне от 0 до 10.")

    if errors:
        raise ValueError("\n".join(errors))


def create_or_update_partner(session: Session, partner: Partner | None, data: dict) -> Partner:
    """
    Создать нового партнёра или обновить существующего
    Если он пустой создаём нового партнёра
    Если он не пустой обновляем его данные
    """
    validate_partner_data(data)

    partner_type_id = data["partner_type_id"]
    name = (data.get("name") or "").strip()
    director = (data.get("director_full_name") or "").strip()
    legal_address = (data.get("legal_address") or "").strip()
    inn = (data.get("inn") or "").strip()
    rating = int(data.get("rating") or 0)

    email = (data.get("email") or "").strip()
    phone_raw = (data.get("phone") or "").strip()

    digits_phone_full = "".join(ch for ch in phone_raw if ch.isdigit())
    digits_phone = ""
    if len(digits_phone_full) >= 11 and digits_phone_full.startswith("7"):
        digits_phone = digits_phone_full[-10:]

    try:
        # Создаём или обновляем самого партнёра
        if partner is None:
            # Новый партнёр
            partner = Partner(
                partner_type_id=partner_type_id,
                name=name,
                director_full_name=director,
                legal_address=legal_address,
                inn=inn,
                rating=rating,
            )
            session.add(partner)
        else:
            # Обновление существующего партнёра
            partner.partner_type_id = partner_type_id
            partner.name = name
            partner.director_full_name = director
            partner.legal_address = legal_address
            partner.inn = inn
            partner.rating = rating

        contact: PartnerContact | None = partner.contacts[0] if partner.contacts else None

        if contact is None and (email or digits_phone):
            contact = PartnerContact(
                partner=partner,
                email=email,
                phone=digits_phone,
            )
            session.add(contact)
        elif contact is not None:
            # Если контакт уже существует обновляем его поля
            contact.email = email
            contact.phone = digits_phone

        session.commit()

    except IntegrityError as e:
        session.rollback()
        msg = str(getattr(e, "orig", e))
        if "partners_inn_key" in msg or '"partners_inn_key"' in msg or '"inn"' in msg:
            raise ValueError("Партнёр с таким ИНН уже существует.")
        raise
    except Exception as e:
        session.rollback()
        print("Неожиданная ошибка при сохранении партнёра:", e)
        raise

    session.refresh(partner)
    return partner


def delete_partner(session: Session, partner: Partner) -> None:
    """
    Удалить партнёра из базы данных
    При удалении: удаляются его контакты и агрегированная запись PartnerSalesSummary
    """
    try:
        session.delete(partner)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise ValueError(
            "Невозможно удалить партнёра, так как с ним связаны другие данные (например, продажи)."
        ) from e
    except Exception as e:
        session.rollback()
        print("Неожиданная ошибка при удалении партнёра:", e)
        raise

