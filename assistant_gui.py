import sys
import os
import json
import logging
import threading
import psutil
import shutil
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLineEdit, QSpinBox,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont

# === Импорт функций и конфига из main_code.py ===
from main_code import (
    speak, listen, execute_command, config, running, save_config
)

# === Настройка логирования ===
logging.basicConfig(
    filename="voice_assis_gui.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Глобальные переменные ===
running = True


# === Класс для перенаправления stdout в QTextEdit ===
class OutputRedirector:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.append(text.strip())

    def flush(self):
        pass


# === Рабочий поток для ассистента (на базе QThread) ===
class AssistantWorker(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        self.status_signal.emit("Активен", "green")
        while not self._stop_flag:
            try:
                text = listen()
                if text and config["wake_word"] in text:
                    cmd = text.replace(config["wake_word"], "").strip()
                    if cmd:
                        self.log_signal.emit(f"[Вы сказали]: {cmd}")
                        execute_command(cmd)
            except Exception as e:
                self.log_signal.emit(f"[Ошибка]: {e}")
                speak("ошибка")
        self.status_signal.emit("Спит", "red")


# === Окно настроек ===
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.layout = QVBoxLayout(self)

        self.fields = {
            "wake_word": QLineEdit(),
            "steam_path": QLineEdit(),
            "volume_step": QSpinBox(),
            "brightness_step": QSpinBox(),
            "telegram_api_hash": QLineEdit(),
            "telegram_api_id": QLineEdit()
        }

        self.fields["wake_word"].setText(config["wake_word"])
        self.fields["steam_path"].setText(config["steam_path"])
        self.fields["volume_step"].setRange(1, 20)
        self.fields["volume_step"].setValue(config["volume_step"])
        self.fields["brightness_step"].setRange(1, 100)
        self.fields["brightness_step"].setValue(config["brightness_step"])
        self.fields["telegram_api_hash"].setText(config["telegram_api_hash"])
        self.fields["telegram_api_id"].setText(str(config["telegram_api_id"]))

        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        save_btn.clicked.connect(self.save_config)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("background-color: #f44336; color: white;")
        cancel_btn.clicked.connect(self.reject)

        self.add_field("Активационная фраза", self.fields["wake_word"])
        self.add_field("Путь к Steam", self.fields["steam_path"], is_path=True)
        self.add_field("Шаг громкости", self.fields["volume_step"])
        self.add_field("Шаг яркости", self.fields["brightness_step"])
        self.add_field("Telegram API HASH", self.fields["telegram_api_hash"])
        self.add_field("Telegram API ID", self.fields["telegram_api_id"])

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(btn_layout)

    def add_field(self, label_text, widget, is_path=False):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        if is_path:
            browse_btn = QPushButton("...")
            browse_btn.clicked.connect(lambda: self.browse_path(widget))
            layout.addWidget(browse_btn)
        self.layout.addLayout(layout)

    def browse_path(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите исполняемый файл Steam")
        if path:
            line_edit.setText(path)

    def save_config(self):
        try:
            config["wake_word"] = self.fields["wake_word"].text().strip()
            config["steam_path"] = self.fields["steam_path"].text().strip()
            config["volume_step"] = self.fields["volume_step"].value()
            config["brightness_step"] = self.fields["brightness_step"].value()
            config["telegram_api_hash"] = self.fields["telegram_api_hash"].text().strip()
            config["telegram_api_id"] = int(self.fields["telegram_api_id"].text().strip())
            save_config()
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Telegram API ID должен быть числом!")


# === Основное окно приложения ===
class AssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пятница — Голосовой Ассистент")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white; font-family: Arial;")

        # === Центральный виджет ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # === Лог-панель ===
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #2b2b2b; border-radius: 5px; padding: 10px;")

        # === Статус-бар ===
        self.status_label = QLabel("Статус: Спит")
        self.status_label.setStyleSheet("font-size: 14px;")

        self.status_circle = QLabel()
        self.status_circle.setFixedSize(20, 20)
        self.status_circle.setStyleSheet("border-radius: 10px; background-color: red;")

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_circle)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # === Кнопки ===
        self.start_btn = QPushButton("Запустить")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.start_btn.clicked.connect(self.toggle_assistant)

        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        self.settings_btn.clicked.connect(self.open_settings)

        self.exit_btn = QPushButton("Выход")
        self.exit_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.exit_btn.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.exit_btn)

        # === Системный мониторинг ===
        self.system_info = QLabel(self.get_system_info())
        self.system_info.setStyleSheet("font-size: 12px; color: #aaa;")
        self.system_info.setWordWrap(True)

        # === Макет ===
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.log_text)
        main_layout.addLayout(status_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.system_info)

        central_widget.setLayout(main_layout)

        # === Таймер обновления системной информации ===
        self.timer = self.startTimer(5000)

        # === Перенаправление stdout ===
        sys.stdout = OutputRedirector(self.log_text)

        # === Рабочий поток ===
        self.worker = AssistantWorker(self)
        self.worker.log_signal.connect(self.on_log_received)  # Подключаем к своему методу
        self.worker.status_signal.connect(self.update_status)

    # === Новый метод для обработки логов ===
    def on_log_received(self, text):
        self.log_text.append(text)

    def timerEvent(self, event):
        self.system_info.setText(self.get_system_info())

    def toggle_assistant(self):
        if self.start_btn.text() == "Запустить":
            self.start_btn.setText("Остановить")
            self.worker.start()
        else:
            self.start_btn.setText("Запустить")
            self.worker.stop()

    def update_status(self, status_text, color):
        self.status_label.setText(f"Статус: {status_text}")
        self.status_circle.setStyleSheet(f"border-radius: 10px; background-color: {color};")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.log_text.append("[Настройки]: Конфигурация обновлена")

    def get_system_info(self):
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            disk_usage = shutil.disk_usage("/")
            disk = (disk_usage.used / disk_usage.total) * 100
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else "N/A"
            return (
                f"CPU: {cpu}%, "
                f"RAM: {ram}%, "
                f"Диск: {disk:.1f}%, "
                f"Батарея: {battery_percent}%"
            )
        except Exception as e:
            logging.error(f"[Ошибка мониторинга]: {e}")
            return "Ошибка получения данных системы"

    def closeEvent(self, event):
        global running
        running = False
        self.worker.stop()
        event.accept()
        sys.exit(0)


# === Запуск приложения ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantGUI()
    window.show()
    sys.exit(app.exec_())