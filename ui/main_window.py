# Главное окно приложения «Модуль работы с партнёрами»

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt

from services.main_window_service import init_session, load_partners, close_session
from ui.partner_dialog import PartnerDialog
from db.models import Partner
from ui.delete_partner_dialog import DeletePartnerDialog
from ui.sales_history_dialog import SalesHistoryDialog
from ui.material_calc_dialog import MaterialCalcDialog


class MainWindow(QMainWindow):
    # Главное окно приложения

    def __init__(self, session_factory, parent=None):
        super().__init__(parent)
        self.session_factory = session_factory
        # Активная сессия БД
        self.session = None
        # Вертикальный layout в который добавляются карточки партнёров
        self.cards_layout = None

        self.init_ui()
        
        # Инициализируем сессию и загружаем партнёров
        init_session(self, self.session_factory)
        load_partners(self)

    def init_ui(self):
        """
        Создаёт и настраивает визуальные элементы главного окна:
            шапка с логотипом, заголовком и блоком кнопок
            прокручиваемая область с карточками партнёров
        """
        self.setWindowTitle("Модуль работы с партнёрами")
        self.setWindowIcon(QIcon("resources/logo.png"))
        self.resize(1000, 700)
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; }")

        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # Верхняя панель логотип + заголовок + блок кнопок
        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Логотип компании
        logo_label = QLabel(header_widget)
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            # Масштабируем логотип с сохранением пропорций
            pixmap = pixmap.scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        # Заголовок главного окна
        title_label = QLabel("Партнёры компании «Мастер пол»", header_widget)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        header_layout.addWidget(
            logo_label,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header_layout.addWidget(
            title_label,
            1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # Блок кнопок вертикальный: добавить / удалить / история / расчёт материала
        btns_widget = QWidget(header_widget)
        btns_layout = QVBoxLayout(btns_widget)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(6)

        btn_add = QPushButton("Добавить партнёра", btns_widget)
        btn_delete = QPushButton("Удалить партнёра", btns_widget)
        btn_history = QPushButton("История реализации", btns_widget)
        btn_calc_material = QPushButton("Расчёт материала", btns_widget)

        font_btn = QFont("Segoe UI", 11)
        font_btn.setBold(True)
        btn_add.setFont(font_btn)
        btn_delete.setFont(font_btn)
        btn_history.setFont(font_btn)
        btn_calc_material.setFont(font_btn)

        # Общий зелёный стиль кнопок
        common_style = """
            QPushButton {
                background-color: #67BA80;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA872;
            }
            QPushButton:pressed {
                background-color: #4C9462;
            }
        """
        btn_add.setStyleSheet(common_style)
        btn_delete.setStyleSheet(common_style)
        btn_history.setStyleSheet(common_style)
        btn_calc_material.setStyleSheet(common_style)

        # Подключаем обработчики нажатий
        btn_add.clicked.connect(self.open_add_partner_dialog)
        btn_delete.clicked.connect(self.open_delete_partner_dialog)
        btn_history.clicked.connect(self.open_sales_history_dialog)
        btn_calc_material.clicked.connect(self.open_material_calc_dialog)

        btns_layout.addWidget(btn_add)
        btns_layout.addWidget(btn_delete)
        btns_layout.addWidget(btn_history)
        btns_layout.addWidget(btn_calc_material)

        header_layout.addWidget(
            btns_widget,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        root_layout.addWidget(header_widget)

        # Прокручиваемая область, внутри которой находится контейнер с карточками
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget(scroll)
        self.cards_layout = QVBoxLayout(container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        # Добавляем stretch чтобы карточки опирались к верху.
        self.cards_layout.addStretch()

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    # Диалоги

    def open_add_partner_dialog(self) -> None:
        # Открытие диалога добавления нового партнёра

        if self.session is None:
            QMessageBox.warning(self, "Добавление партнёра", "Нет подключения к базе данных.", QMessageBox.StandardButton.Ok,)
            return

        dlg = PartnerDialog(self.session, partner=None, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            load_partners(self)

    def open_edit_partner_dialog(self, partner: Partner) -> None:
        # Открытие диалога редактирования существующего партнёра при нажатии на карточку

        if self.session is None:
            QMessageBox.warning(self, "Редактирование партнёра", "Нет подключения к базе данных.", QMessageBox.StandardButton.Ok,)
            return

        dlg = PartnerDialog(self.session, partner=partner, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            load_partners(self)

    def open_delete_partner_dialog(self) -> None:
        # Открытие диалога удаления партнёра
        
        if self.session is None:
            QMessageBox.warning(self, "Удаление партнёра", "Нет подключения к базе данных.", QMessageBox.StandardButton.Ok,)
            return

        dlg = DeletePartnerDialog(self.session, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            load_partners(self)

    def open_sales_history_dialog(self) -> None:
        # Открытие окна истории реализации продукции
        
        if self.session is None:
            QMessageBox.warning(self, "История", "Нет подключения к базе данных.", QMessageBox.StandardButton.Ok,)
            return

        dlg = SalesHistoryDialog(self.session, self)
        dlg.exec()

    def open_material_calc_dialog(self) -> None:
        # Открытие окна расчёта количества материала
        
        if self.session is None:
            QMessageBox.warning(self, "Расчёт материала", "Нет подключения к базе данных.", QMessageBox.StandardButton.Ok,)
            return

        dlg = MaterialCalcDialog(self.session, self)
        dlg.exec()

    # События
    def closeEvent(self, event):
        # Переопределение события закрытия окна
        
        close_session(self)
        super().closeEvent(event)
