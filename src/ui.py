import sys
from PySide2.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QKeySequenceEdit, \
    QPushButton


class TalkGPTGui(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.gpt_mode_label = QLabel('Select GPT mode:')
        layout.addWidget(self.gpt_mode_label)

        self.gpt_mode_combobox = QComboBox()
        self.gpt_mode_combobox.addItem('Standard')
        self.gpt_mode_combobox.addItem('Advanced')
        self.gpt_mode_combobox.currentIndexChanged.connect(self.update_gpt_mode)
        layout.addWidget(self.gpt_mode_combobox)

        self.key_binding_label = QLabel('Select Hot Key:')
        layout.addWidget(self.key_binding_label)

        self.key_binding_edit = QKeySequenceEdit()
        layout.addWidget(self.key_binding_edit)

        self.update_hot_key_button = QPushButton('Update Hot Key')
        self.update_hot_key_button.clicked.connect(self.update_hot_key)
        layout.addWidget(self.update_hot_key_button)

    def update_gpt_mode(self):
        mode = self.gpt_mode_combobox.currentText()
        self.app.worker.generator.mode = mode

    def update_hot_key(self):
        hot_key = self.key_binding_edit.keySequence().toString()
        self.app.producer.hot_key = hot_key


