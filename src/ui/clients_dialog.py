from PyQt6 import QtWidgets, QtCore

from ..core.clients import ClientStorage, Client


class ClientsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clientes")
        self.resize(520, 420)
        self.storage = ClientStorage()
        self.selected_client: Client | None = None
        self._init_ui()
        self._load()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nome ou telefone…")
        btn_search = QtWidgets.QPushButton("Buscar")
        btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nome", "Telefone", "Email", "Total Gasto (R$)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        btns = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("+ Adicionar")
        self.btn_edit = QtWidgets.QPushButton("✏️ Editar")
        self.btn_remove = QtWidgets.QPushButton("- Remover")
        self.btn_select = QtWidgets.QPushButton("Selecionar")
        self.btn_edit.setEnabled(False)
        self.btn_remove.setEnabled(False)
        self.btn_select.setEnabled(False)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_remove.clicked.connect(self._on_remove)
        self.btn_select.clicked.connect(self._on_select)
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_remove)
        btns.addStretch(1)
        btns.addWidget(self.btn_select)
        layout.addLayout(btns)

        self.table.itemSelectionChanged.connect(self._toggle_actions)

    def _toggle_actions(self):
        has = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has)
        self.btn_remove.setEnabled(has)
        self.btn_select.setEnabled(has)

    def _load(self):
        clients = self.storage.list_clients()
        self._fill(clients)

    def _fill(self, clients: list[Client]):
        self.table.setRowCount(len(clients))
        for r, c in enumerate(clients):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(c.name))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(c.phone))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(c.email or ""))
            self.table.setItem(r, 3, QtWidgets.QTableWidgetItem(f"{c.total_spent:.2f}"))
        self.table.resizeColumnsToContents()

    def _on_search(self):
        term = self.search_input.text().strip()
        if term:
            clients = self.storage.find_by_name_or_phone(term)
        else:
            clients = self.storage.list_clients()
        self._fill(clients)

    def _on_add(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Novo Cliente", "Nome:")
        if not ok or not name.strip():
            return
        phone, ok = QtWidgets.QInputDialog.getText(self, "Novo Cliente", "Telefone:")
        if not ok:
            return
        email, ok = QtWidgets.QInputDialog.getText(self, "Novo Cliente", "Email:")
        if not ok:
            email = ""
        self.storage.create_client(name=name.strip(), phone=phone.strip(), email=email.strip() or None)
        self._load()

    def _get_selected_client(self) -> Client | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        name = self.table.item(row, 0).text()
        phone = self.table.item(row, 1).text()
        email = self.table.item(row, 2).text().strip() or None
        # resolve por busca
        matches = self.storage.find_by_name_or_phone(phone or name)
        return matches[0] if matches else None

    def _on_edit(self):
        c = self._get_selected_client()
        if not c:
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Editar Cliente", "Nome:", text=c.name)
        if not ok or not name.strip():
            return
        phone, ok = QtWidgets.QInputDialog.getText(self, "Editar Cliente", "Telefone:", text=c.phone)
        if not ok:
            return
        email, ok = QtWidgets.QInputDialog.getText(self, "Editar Cliente", "Email:", text=c.email or "")
        if not ok:
            return
        c.name = name.strip()
        c.phone = phone.strip()
        c.email = email.strip() or None
        self.storage.update_client(c)
        self._load()

    def _on_remove(self):
        c = self._get_selected_client()
        if not c:
            return
        self.storage.delete_client(c.id)
        self._load()

    def _on_select(self):
        c = self._get_selected_client()
        if not c:
            return
        self.selected_client = c
        self.accept()

    def get_selected(self) -> Client | None:
        return self.selected_client


