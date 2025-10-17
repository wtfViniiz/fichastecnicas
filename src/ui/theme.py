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


