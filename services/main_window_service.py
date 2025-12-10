# Сервисные функции для главного окна приложения

from sqlalchemy.orm import Session
from PyQt6.QtWidgets import QMessageBox
from db.models import Partner
from ui.partner_card import PartnerCard

def init_session(window, session_factory):
    # Инициализирует сессию БД для главного окна
    try:
        window.session = session_factory()
    except Exception as e:
        window.session = None
        QMessageBox.critical(window, "Ошибка подключения", f"Не удалось установить подключение к базе данных:\n{e}", QMessageBox.StandardButton.Ok,)

def close_session(window):
    # Закрывает сессию привязанную к окну
    if isinstance(getattr(window, "session", None), Session):
        try:
            window.session.close()
        except Exception as e:
            print("Ошибка при закрытии сессии БД:", e)
    window.session = None


def clear_cards(window):
    """
    Удаляет все карточки партнёров из контейнера главного окна кроме последнего контейнера-элемента
    используется перед повторной загрузкой списка партнёров
    """
    layout = window.cards_layout
    if layout is None:
        return

    while layout.count() > 1:
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()


def load_partners(window):
    """
    Загружает из БД список партнёров, сортируя по рейтингу (по убыванию)
    и наименованию, и создаёт для каждого карточку PartnerCard.
    """
    session = getattr(window, "session", None)
    layout = window.cards_layout
    if session is None or layout is None:
        return
    
    # Очищаем текущие карточки.
    clear_cards(window)
    try:
        partners = (
            session.query(Partner)
            .order_by(Partner.rating.desc(), Partner.name)
            .all()
        )
    except Exception as e:
        QMessageBox.critical(window, "Ошибка загрузки данных", f"Не удалось загрузить список партнёров из базы данных:\n{e}", QMessageBox.StandardButton.Ok,)
        return

    # Для каждого партнёра создаём карточку и добавляем её в layout
    for partner in partners:
        try:
            card = PartnerCard(partner, on_click=window.open_edit_partner_dialog, parent=window,)
            layout.insertWidget(layout.count() - 1, card)
        except Exception as e:
            print(f"Ошибка при создании карточки для партнёра '{partner.name}':", e)
