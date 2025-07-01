import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QTabWidget, QStatusBar, QToolBar, QLabel, QLineEdit,
    QPushButton, QDialog, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtGui import (
    QAction, QIcon, QKeySequence, QTextCharFormat, QSyntaxHighlighter,
    QFont, QColor
)
from PyQt6.QtCore import Qt, QRegularExpression, QSize


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        kw_format = QTextCharFormat()
        kw_format.setForeground(QColor("#569CD6"))
        kw_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'try', 'while', 'with', 'yield'
        ]
        for kw in keywords:
            pattern = QRegularExpression(r'\b' + kw + r'\b')
            self.rules.append((pattern, kw_format))

        str_format = QTextCharFormat()
        str_format.setForeground(QColor("#D69D85"))
        self.rules.append((QRegularExpression(r'".*?"'), str_format))
        self.rules.append((QRegularExpression(r"'.*?'"), str_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r'#.*'), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class TextEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.highlighter = PythonHighlighter(self.document())
        font = QFont("Consolas", 13)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E2F;
                color: #D4D4D4;
                border-radius: 12px;
                padding: 18px;
                selection-background-color: #264F78;
                font-weight: 500;
                font-family: Consolas, monospace;
            }
            QTextEdit:hover {
                background-color: #2A2A40;
            }
        """)


class FindReplaceDialog(QDialog):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Найти и заменить")
        self.setFixedSize(500, 150)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            background: #252536;
            border-radius: 18px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #D4D4D4;
        """)

        layout = QVBoxLayout(self)

        find_layout = QHBoxLayout()
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Что найти")
        self.find_input.setStyleSheet(self.input_style())
        find_layout.addWidget(self.find_input)

        self.find_btn = QPushButton("Найти далее")
        self.find_btn.setFixedWidth(130)
        self.find_btn.setStyleSheet(self.button_style("#007ACC"))
        find_layout.addWidget(self.find_btn)
        layout.addLayout(find_layout)

        replace_layout = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Заменить на")
        self.replace_input.setStyleSheet(self.input_style())
        replace_layout.addWidget(self.replace_input)

        self.replace_btn = QPushButton("Заменить")
        self.replace_btn.setFixedWidth(130)
        self.replace_btn.setStyleSheet(self.button_style("#0E639C"))
        replace_layout.addWidget(self.replace_btn)

        self.replace_all_btn = QPushButton("Заменить всё")
        self.replace_all_btn.setFixedWidth(130)
        self.replace_all_btn.setStyleSheet(self.button_style("#C586C0"))
        replace_layout.addWidget(self.replace_all_btn)

        layout.addLayout(replace_layout)

        self.find_btn.clicked.connect(self.find_next)
        self.replace_btn.clicked.connect(self.replace_one)
        self.replace_all_btn.clicked.connect(self.replace_all)

    def input_style(self):
        return """
            background-color: #1E1E2F;
            border: 1.8px solid #3C3C54;
            border-radius: 10px;
            padding: 9px 12px;
            font-size: 15px;
            color: #D4D4D4;
        """

    def button_style(self, color):
        return f"""
            background-color: {color};
            color: #EEE;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 15px;
            padding: 10px 18px;
            margin-left: 12px;
        """

    def find_next(self):
        text = self.find_input.text()
        if not text:
            return
        cursor = self.editor.textCursor()
        pos = cursor.position()
        found = self.editor.document().find(text, pos)
        if found.isNull():
            found = self.editor.document().find(text, 0)
            if found.isNull():
                QMessageBox.information(self, "Поиск", "Ничего не найдено")
                return
        self.editor.setTextCursor(found)

    def replace_one(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        text = self.find_input.text()
        replacement = self.replace_input.text()
        content = self.editor.toPlainText()
        self.editor.setPlainText(content.replace(text, replacement))


class DeShakTyper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeShak Typer — Тёмный, ультра красивый редактор")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #121212;")

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #1E1E2F;
                color: #BBB;
                padding: 10px 22px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                margin-right: 3px;
                font-weight: 600;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #3A3A56;
                color: #FFF;
            }
            QTabBar::tab:hover {
                background: #2C2C42;
            }
        """)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("""
            QStatusBar {
                background-color: #1E1E2F;
                color: #DDD;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 15px;
            }
        """)

        self.status_cursor = QLabel("Строка: 1, Столбец: 1")
        self.status_words = QLabel("Слов: 0")
        self.status.addPermanentWidget(self.status_words)
        self.status.addPermanentWidget(self.status_cursor)

        self.create_actions()
        self.create_menu()
        self.init_toolbar()
        self.new_tab()

    def create_actions(self):
        self.new_action = QAction(QIcon.fromTheme("document-new"), "Новый", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_tab)

        self.open_action = QAction(QIcon.fromTheme("document-open"), "Открыть...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction(QIcon.fromTheme("document-save"), "Сохранить", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_file)

        self.exit_action = QAction("Выход", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)

        self.find_action = QAction(QIcon.fromTheme("edit-find"), "Найти и заменить", self)
        self.find_action.setShortcut(QKeySequence("Ctrl+F"))
        self.find_action.triggered.connect(self.open_find_dialog)

        self.run_action = QAction("Запустить код", self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.triggered.connect(self.run_code)

        self.premium_buy_action = QAction("Купить Премиум", self)
        self.premium_buy_action.triggered.connect(self.premium_buy_clicked)

        self.premium_switch_action = QAction("Переключиться на Премиум", self)
        self.premium_switch_action.triggered.connect(self.premium_switch_clicked)

    def create_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #1E1E2F; color: #DDD;")

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menubar.addMenu("Правка")
        edit_menu.addAction(self.find_action)

        run_menu = menubar.addMenu("Выполнить")
        run_menu.addAction(self.run_action)

        premium_menu = menubar.addMenu("Премиум")
        premium_menu.addAction(self.premium_buy_action)
        premium_menu.addAction(self.premium_switch_action)

    def init_toolbar(self):
        self.toolbar = self.addToolBar("Основное меню")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(28, 28))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: #1E1E2F;
                border-bottom: 1px solid #3C3C54;
                padding: 8px 16px;
            }
            QToolButton {
                background: transparent;
                border-radius: 8px;
                padding: 8px;
                margin-right: 10px;
                color: #AAA;
                font-weight: 600;
            }
            QToolButton:hover {
                color: #569CD6;
                background: #2A2A40;
            }
        """)
        for action in (
            self.new_action, self.open_action, self.save_action,
            self.find_action, self.run_action,
            self.premium_buy_action, self.premium_switch_action
        ):
            self.toolbar.addAction(action)

    def current_editor(self):
        return self.tabs.currentWidget()

    def new_tab(self):
        editor = TextEditor()
        editor.textChanged.connect(self.update_status)
        editor.cursorPositionChanged.connect(self.update_status)
        editor.path = None
        self.tabs.addTab(editor, "Новый файл")
        self.tabs.setCurrentWidget(editor)
        self.update_status()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Текстовые файлы (*.txt *.py *.md);;Все файлы (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
                return
            editor = TextEditor()
            editor.setPlainText(content)
            editor.path = path
            self.tabs.addTab(editor, path.split("/")[-1])
            self.tabs.setCurrentWidget(editor)
            self.update_status()

    def save_file(self):
        editor = self.current_editor()
        if not editor:
            return
        if not getattr(editor, 'path', None):
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Текст (*.txt *.py);;Все файлы (*)")
            if not path:
                return
            editor.path = path
            self.tabs.setTabText(self.tabs.currentIndex(), path.split("/")[-1])
        try:
            with open(editor.path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
            return
        self.status.showMessage(f"Сохранено: {editor.path}", 3500)

    def open_find_dialog(self):
        editor = self.current_editor()
        if editor:
            dlg = FindReplaceDialog(self, editor)
            dlg.exec()

    def update_status(self):
        editor = self.current_editor()
        if not editor:
            self.status_cursor.setText("Строка: -, Столбец: -")
            self.status_words.setText("Слов: 0")
            return
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        text = editor.toPlainText()
        words = len(text.split())
        self.status_cursor.setText(f"Строка: {line}, Столбец: {col}")
        self.status_words.setText(f"Слов: {words}")

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def run_code(self):
        # Здесь можно добавить выполнение кода, сейчас просто сообщение
        QMessageBox.information(self, "Выполнить", "Функция запуска кода пока не реализована.")

    def premium_buy_clicked(self):
        QMessageBox.information(self, "Премиум", "Покупка премиума пока недоступна.")

    def premium_switch_clicked(self):
        QMessageBox.information(self, "Премиум", "Переключение на премиум пока недоступно.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DeShakTyper()
    window.show()
    sys.exit(app.exec())
