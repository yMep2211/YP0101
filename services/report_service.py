"""
Сервис формирования PDF-отчётов
Содержит:
    generate_partner_sales_report: отчёт по истории реализации продукции партнёра
    generate_material_calc_report: отчёт по результатам расчёта количества материала
"""

from sqlalchemy.orm import Session
from db.models import Partner, ProductType, MaterialType
from services.sales_history_service import get_partner_sales
from services.calculation_service import calculate_required_material

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Имена шрифтов, под которыми они регистрируются в reportlab
FONT_NAME = "DejaVuSans"
FONT_BOLD_NAME = "DejaVuSans-Bold"

# Путь к TTF-файлу с поддержкой кириллицы
FONT_PATH = "resources/DejaVuSans.ttf"

def _register_fonts() -> None:
    # Регистрирует TTF-шрифт с поддержкой кириллицы в reportlab

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # если уже зарегистрирован ничего не делаем
    try:
        pdfmetrics.getFont(FONT_NAME)
        return
    except KeyError:
        pass

    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
        pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, FONT_PATH))
    except Exception as e:
        # Если шрифт не найден или битый отчёт не сформируется корректно.
        raise RuntimeError(
            f"Не удалось зарегистрировать шрифт '{FONT_NAME}'. "
            f"Убедитесь, что файл '{FONT_PATH}' существует и доступен.\n{e}"
        ) from e


def _format_phone(phone_digits: str | None) -> str:
   # Приводит телефон из строки цифр к формату +7XXXXXXXXXX
    if not phone_digits:
        return ""
    digits = "".join(ch for ch in phone_digits if ch.isdigit())
    if len(digits) == 10:
        return f"+7{digits}"
    if len(digits) == 11 and digits.startswith("7"):
        return f"+7{digits[1:]}"
    return digits


def _calculate_discount(total_qty: float) -> int:
    """
    Расчёт скидки в зависимости от общего объёма продаж партнёра
    Пороговые значения : до 10000 – 0%, от 10000 – до 50000 – 5%, от 50000 – до 300000 – 10%, более 300000 – 15%.
    """
    if total_qty < 10000:
        return 0
    if total_qty < 50000:
        return 3
    if total_qty < 100000:
        return 5
    if total_qty < 500000:
        return 7
    return 10


def generate_partner_sales_report(session: Session, partner_id: int, filename: str) -> None:
    """
    Формирует PDF-отчёт по истории реализации продукции выбранного партнёра
    В отчёт включаются:
        заголовок: «История реализации продукции»
        тип партнёра, наименование, рейтинг
        телефон, email
        суммарный объём реализации и скидка
        таблица: дата продажи, продукция, количество
    """

    # регистрируем шрифты с кириллицей
    _register_fonts()

    # получаем партнёра
    try:
        partner: Partner | None = session.get(Partner, partner_id)
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении данных о партнёре из базы данных:\n{e}") from e

    if partner is None:
        raise ValueError("Партнёр с указанным идентификатором не найден.")

    # тип партнёра
    partner_type_name = ""
    if hasattr(partner, "partner_type") and partner.partner_type is not None:
        partner_type_name = partner.partner_type.name or ""

    # контактные данные
    email = ""
    phone_digits = ""
    if getattr(partner, "contacts", None):
        contact = partner.contacts[0]
        email = contact.email or ""
        phone_digits = contact.phone or ""

    phone_formatted = _format_phone(phone_digits)
    rating = getattr(partner, "rating", None) or 0

    # история продаж
    try:
        sales = get_partner_sales(session, partner.id)
    except Exception as e:
        raise RuntimeError(f"Не удалось получить историю продаж партнёра:\n{e}") from e

    total_quantity = 0.0
    for _, _, quantity in sales:
        if quantity is not None:
            try:
                total_quantity += float(quantity)
            except (TypeError, ValueError):
                # Если вдруг в БД оказались некорректные данные по количеству пропускаем
                pass

    discount = _calculate_discount(total_quantity)

    # собираем документ через platypus 
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    base_styles = getSampleStyleSheet()

    # свои стили с уникальными именами
    body_style = ParagraphStyle(
        name="BodyRus",
        parent=base_styles["Normal"],
        fontName=FONT_NAME,
        fontSize=11,
        leading=14,
    )
    body_bold_style = ParagraphStyle(
        name="BodyRusBold",
        parent=base_styles["Normal"],
        fontName=FONT_BOLD_NAME,
        fontSize=11,
        leading=14,
    )
    title_style = ParagraphStyle(
        name="TitleRus",
        parent=base_styles["Heading1"],
        fontName=FONT_BOLD_NAME,
        fontSize=18,
        leading=22,
        alignment=1,
    )

    elems = []

    # заголовок
    elems.append(Paragraph("История реализации продукции", title_style))
    elems.append(Spacer(1, 12))

    # блок с информацией о партнёре
    info_lines = [
        f"Тип партнёра: {partner_type_name}",
        f"Наименование партнёра: {partner.name or ''}",
        f"Рейтинг: {rating}",
        f"Телефон: {phone_formatted}",
        f"Email: {email}",
        f"Суммарный объём реализации (м²): {int(total_quantity)}",
        f"Скидка: {discount} %",
    ]
    for line in info_lines:
        elems.append(Paragraph(line, body_style))
    elems.append(Spacer(1, 18))

    # заголовок таблицы
    elems.append(Paragraph("Таблица продаж", body_bold_style))
    elems.append(Spacer(1, 6))

    # данные таблицы: шапка
    table_data = [
        ["Дата продажи", "Продукция", "Количество (м²)"]
    ]
    # строки с продажами
    for sale_date, product_name, quantity in sales:
        date_str = sale_date.strftime("%d.%m.%Y") if hasattr(sale_date, "strftime") else str(sale_date)
        name_str = product_name or ""
        qty_str = str(quantity)
        table_data.append([date_str, name_str, qty_str])

    # если продаж нет — добавляем строку заглушку
    if len(table_data) == 1:
        table_data.append(["-", "Нет данных о продажах", "-"])

    # создаём таблицу
    table = Table(
        table_data,
        colWidths=[90, 325, 100],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        # шапка
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4E8D3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD_NAME),
        ("FONTSIZE", (0, 0), (-1, 0), 11),

        # выравнивание заголовков по центру
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        # тело
        ("FONTNAME", (0, 1), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 1), (-1, -1), 10),

        # выравнивание тела: даты и продукция слева, количество справа
        ("ALIGN", (0, 1), (0, -1), "LEFT"),   # даты
        ("ALIGN", (1, 1), (1, -1), "LEFT"),   # продукция
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),  # количество

        # линии
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),

        # отступы
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    elems.append(table)

    # собираем PDF
    try:
        doc.build(elems)
    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании PDF-отчёта по партнёру:\n{e}") from e


def generate_material_calc_report(session: Session, product_type_id: int, material_type_id: int, quantity: int, param1: float, param2: float, filename: str,) -> None:
    """
    Формирует PDF-отчёт по расчёту количества материала
    В отчёт включаются:
        заголовок: «Расчёт количества материала»
        выбранный тип продукции и тип материала
        входные параметры
        результат расчёта
    Отчёт формируется даже при ошибке расчёта в этом случае выводится текст с пояснением
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except Exception as e:
        raise RuntimeError(
            "Для формирования PDF-отчёта необходим пакет reportlab.\n"
            "Установите его командой:\n\npip install reportlab"
        ) from e

    # регистрируем шрифты
    _register_fonts()

    # пробуем найти типы продукции и материала в БД
    try:
        product_type = session.get(ProductType, product_type_id)
        material_type = session.get(MaterialType, material_type_id)
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении данных из БД для расчёта материала:\n{e}") from e

    product_type_name = product_type.name if product_type is not None else "Не найден"
    material_type_name = material_type.name if material_type is not None else "Не найден"

    # сам расчёт (может вернуть -1 при ошибке входных данных)
    try:
        result = calculate_required_material(session, product_type_id, material_type_id, quantity, param1, param2,)
    except Exception as e:
        result = -1
        print("Ошибка при расчёте количества материала:", e)

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    base_styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        name="BodyRusCalc",
        parent=base_styles["Normal"],
        fontName=FONT_NAME,
        fontSize=11,
        leading=14,
    )
    body_bold_style = ParagraphStyle(
        name="BodyRusCalcBold",
        parent=base_styles["Normal"],
        fontName=FONT_BOLD_NAME,
        fontSize=11,
        leading=14,
    )
    title_style = ParagraphStyle(
        name="TitleRusCalc",
        parent=base_styles["Heading1"],
        fontName=FONT_BOLD_NAME,
        fontSize=18,
        leading=22,
        alignment=1,
    )

    elems = []

    elems.append(Paragraph("Расчёт количества материала", title_style))
    elems.append(Spacer(1, 12))

    elems.append(Paragraph(f"Тип продукции: {product_type_name}", body_style))
    elems.append(Paragraph(f"Тип материала: {material_type_name}", body_style))
    elems.append(Spacer(1, 12))

    elems.append(Paragraph(f"Количество продукции, шт.: {quantity}", body_style))
    elems.append(Paragraph(f"Параметр 1: {param1}", body_style))
    elems.append(Paragraph(f"Параметр 2: {param2}", body_style))
    elems.append(Spacer(1, 12))

    if result >= 0:
        elems.append(Paragraph(
            f"Результат расчёта: необходимо {result} условных единиц материала.",
            body_bold_style
        ))
    else:
        elems.append(Paragraph(
            "Результат расчёта: невозможно выполнить расчёт с указанными параметрами "
            "(проверьте выбранные типы, количество и параметры).",
            body_bold_style
        ))

    try:
        doc.build(elems)
    except Exception as e:
        raise RuntimeError(f"Ошибка при формировании PDF-отчёта по расчёту материала:\n{e}") from e
