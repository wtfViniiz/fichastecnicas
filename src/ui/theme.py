from PyQt6 import QtWidgets, QtGui, QtCore


class ThemeManager:
    """Gerencia tema claro/escuro com persistência em QSettings."""

    SETTINGS_ORG = "ManauaraDesign"
    SETTINGS_APP = "BudgetApp"
    SETTINGS_KEY = "theme"

    @classmethod
    def current_theme(cls) -> str:
        settings = QtCore.QSettings(cls.SETTINGS_ORG, cls.SETTINGS_APP)
        theme = settings.value(cls.SETTINGS_KEY, "light")
        return str(theme)

    @classmethod
    def save_theme(cls, theme: str) -> None:
        settings = QtCore.QSettings(cls.SETTINGS_ORG, cls.SETTINGS_APP)
        settings.setValue(cls.SETTINGS_KEY, theme)

    @classmethod
    def apply_theme(cls, app: QtWidgets.QApplication, theme: str) -> None:
        # Usa estilo Fusion para melhor consistência entre temas
        app.setStyle("Fusion")
        palette = QtGui.QPalette()
        if theme == "dark":
            # Baseado no dark palette do Qt
            palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(35, 35, 35))
            palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 0, 0))
            palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
            palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
            palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
        else:
            palette = app.style().standardPalette()

        app.setPalette(palette)
        cls.save_theme(theme)
        # Aplica QSS moderno para suavizar UI
        app.setStyleSheet(cls._modern_qss(theme))

    @classmethod
    def apply_saved_theme(cls, app: QtWidgets.QApplication) -> str:
        theme = cls.current_theme()
        cls.apply_theme(app, theme)
        return theme

    @classmethod
    def toggle_theme(cls, app: QtWidgets.QApplication) -> str:
        theme = cls.current_theme()
        new_theme = "dark" if theme != "dark" else "light"
        cls.apply_theme(app, new_theme)
        return new_theme

    @staticmethod
    def _modern_qss(theme: str) -> str:
        radius = 8
        if theme == "dark":
            bg = "#353535"
            card = "#2b2b2b"
            border = "#444"
            text = "#f0f0f0"
            primary = "#2a82da"
            hover = "#3a92ea"
        else:
            bg = "#f6f7fb"
            card = "#ffffff"
            border = "#dcdfe6"
            text = "#1f2d3d"
            primary = "#2a82da"
            hover = "#3a92ea"
        return f"""
        QWidget {{
            color: {text};
            background: {bg};
            font-size: 13px;
        }}
        QGroupBox {{
            background: {card};
            border: 1px solid {border};
            border-radius: {radius}px;
            margin-top: 12px;
            padding-top: 12px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            color: {text};
            font-weight: 600;
        }}
        QPushButton {{
            background: {primary};
            color: white;
            border-radius: {radius}px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:disabled {{ background: {border}; color: #999; }}
        QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background: {card};
            border: 1px solid {border};
            border-radius: {radius}px;
            padding: 6px 8px;
        }}
        QListWidget, QTableWidget {{
            background: {card};
            border: 1px solid {border};
            border-radius: {radius}px;
        }}
        QTabWidget::pane {{
            border: 1px solid {border};
            border-radius: {radius}px;
            background: {card};
        }}
        QToolBar {{
            background: {card};
            border-bottom: 1px solid {border};
            padding: 4px;
        }}
        QStatusBar {{ background: transparent; }}
        """


