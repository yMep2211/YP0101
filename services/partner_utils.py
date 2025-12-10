# вспомогательные функции для рассчета скидки и формата телефона

def format_phone(raw: str) -> str:
    # Приводит номер телефона к виду +7XXXXXXXXXX
    digits = "".join(ch for ch in raw if ch.isdigit())

    if len(digits) == 11 and digits.startswith("8"):
        return "+7" + digits[1:]
    if len(digits) == 11 and digits.startswith("7"):
        return "+7" + digits[1:]
    if len(digits) == 10:
        return "+7" + digits

    if digits:
        # Если цифр больше 10, берём последние 10 предпологая что это и есть номер
        return "+7" + digits[-10:]

    return raw


def calc_discount(total_qty: int) -> int:
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