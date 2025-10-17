from PyQt6 import QtWidgets, QtGui, QtCore
from datetime import date, datetime
from typing import List, Dict, Optional

from ..core.budget_storage import BudgetStorage


class BudgetSearchDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscar Orçamentos")
        self.resize(800, 600)
        self.storage = BudgetStorage()
        self.selected_budget = None
        self._init_ui()
        self._load_recent_budgets()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Filtros de busca
        filters_group = QtWidgets.QGroupBox("Filtros de Busca")
        filters_layout = QtWidgets.QGridLayout(filters_group)
        
        # Nome do cliente
        filters_layout.addWidget(QtWidgets.QLabel("Nome do Cliente:"), 0, 0)
        self.client_name_input = QtWidgets.QLineEdit()
        self.client_name_input.setPlaceholderText("Digite o nome do cliente...")
        filters_layout.addWidget(self.client_name_input, 0, 1)
        
        # Data de
        filters_layout.addWidget(QtWidgets.QLabel("Data de:"), 1, 0)
        self.date_from = QtWidgets.QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QtCore.QDate.currentDate().addDays(-30))
        filters_layout.addWidget(self.date_from, 1, 1)
        
        # Data até
        filters_layout.addWidget(QtWidgets.QLabel("Data até:"), 1, 2)
        self.date_to = QtWidgets.QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QtCore.QDate.currentDate())
        filters_layout.addWidget(self.date_to, 1, 3)
        
        # Botões de busca
        search_buttons = QtWidgets.QHBoxLayout()
        self.search_btn = QtWidgets.QPushButton("Buscar")
        self.search_btn.clicked.connect(self._search_budgets)
        self.clear_btn = QtWidgets.QPushButton("Limpar")
        self.clear_btn.clicked.connect(self._clear_filters)
        search_buttons.addWidget(self.search_btn)
        search_buttons.addWidget(self.clear_btn)
        search_buttons.addStretch(1)
        filters_layout.addLayout(search_buttons, 2, 0, 1, 4)
        
        layout.addWidget(filters_group)
        
        # Lista de resultados
        results_group = QtWidgets.QGroupBox("Resultados")
        results_layout = QtWidgets.QVBoxLayout(results_group)
        
        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Data", "Total", "Itens", "Ações"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.itemDoubleClicked.connect(self._on_double_click)
        results_layout.addWidget(self.results_table)
        
        # Botões de ação
        action_buttons = QtWidgets.QHBoxLayout()
        self.load_btn = QtWidgets.QPushButton("Carregar Selecionado")
        self.load_btn.clicked.connect(self._load_selected)
        self.load_btn.setEnabled(False)
        self.delete_btn = QtWidgets.QPushButton("Excluir Selecionado")
        self.delete_btn.clicked.connect(self._delete_selected)
        self.delete_btn.setEnabled(False)
        action_buttons.addWidget(self.load_btn)
        action_buttons.addWidget(self.delete_btn)
        action_buttons.addStretch(1)
        results_layout.addLayout(action_buttons)
        
        layout.addWidget(results_group)
        
        # Botões do diálogo
        dialog_buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | 
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.accepted.connect(self._on_ok)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)
        
        # Conectar seleção
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_recent_budgets(self):
        """Carrega orçamentos recentes"""
        recent = self.storage.get_recent_budgets(20)
        self._populate_table(recent)

    def _search_budgets(self):
        """Executa busca com filtros"""
        client_name = self.client_name_input.text().strip()
        date_from = self.date_from.date().toString("yyyy-MM-dd") if self.date_from.date().isValid() else ""
        date_to = self.date_to.date().toString("yyyy-MM-dd") if self.date_to.date().isValid() else ""
        
        results = self.storage.search_budgets(client_name, date_from, date_to)
        self._populate_table(results)

    def _clear_filters(self):
        """Limpa filtros e carrega orçamentos recentes"""
        self.client_name_input.clear()
        self.date_from.setDate(QtCore.QDate.currentDate().addDays(-30))
        self.date_to.setDate(QtCore.QDate.currentDate())
        self._load_recent_budgets()

    def _populate_table(self, budgets: List[Dict]):
        """Preenche tabela com resultados"""
        self.results_table.setRowCount(len(budgets))
        
        for row, budget in enumerate(budgets):
            # ID
            self.results_table.setItem(row, 0, QtWidgets.QTableWidgetItem(budget["id"]))
            
            # Cliente
            client_name = budget["client"]["name"]
            self.results_table.setItem(row, 1, QtWidgets.QTableWidgetItem(client_name))
            
            # Data
            created_date = budget["created_date"]
            self.results_table.setItem(row, 2, QtWidgets.QTableWidgetItem(created_date))
            
            # Total
            total = f"R$ {budget['total']:.2f}"
            self.results_table.setItem(row, 3, QtWidgets.QTableWidgetItem(total))
            
            # Itens
            items_count = len(budget["items"])
            self.results_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(items_count)))
            
            # Ações
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QtWidgets.QPushButton("Ver")
            view_btn.clicked.connect(lambda checked, bid=budget["id"]: self._view_budget(bid))
            actions_layout.addWidget(view_btn)
            
            self.results_table.setCellWidget(row, 5, actions_widget)
        
        # Ajustar largura das colunas
        self.results_table.resizeColumnsToContents()

    def _view_budget(self, budget_id: str):
        """Visualiza detalhes de um orçamento"""
        budget = self.storage.load_budget(budget_id)
        if budget:
            dialog = BudgetDetailsDialog(budget, self)
            dialog.exec()

    def _on_selection_changed(self):
        """Habilita/desabilita botões baseado na seleção"""
        has_selection = len(self.results_table.selectedItems()) > 0
        self.load_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def _on_double_click(self, item):
        """Carrega orçamento ao clicar duas vezes"""
        if item:
            self._load_selected()

    def _load_selected(self):
        """Carrega orçamento selecionado"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            budget_id = self.results_table.item(current_row, 0).text()
            self.selected_budget = self.storage.load_budget(budget_id)
            self.accept()

    def _delete_selected(self):
        """Exclui orçamento selecionado"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            budget_id = self.results_table.item(current_row, 0).text()
            client_name = self.results_table.item(current_row, 1).text()
            
            reply = QtWidgets.QMessageBox.question(
                self, "Confirmar Exclusão",
                f"Deseja realmente excluir o orçamento {budget_id} do cliente {client_name}?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                if self.storage.delete_budget(budget_id):
                    QtWidgets.QMessageBox.information(self, "Sucesso", "Orçamento excluído com sucesso.")
                    self._load_recent_budgets()
                else:
                    QtWidgets.QMessageBox.warning(self, "Erro", "Erro ao excluir orçamento.")

    def _on_ok(self):
        """Confirma seleção"""
        if self.selected_budget:
            self.accept()
        else:
            self.reject()

    def get_selected_budget(self):
        """Retorna orçamento selecionado"""
        return self.selected_budget


class BudgetDetailsDialog(QtWidgets.QDialog):
    def __init__(self, budget, parent=None):
        super().__init__(parent)
        self.budget = budget
        self.setWindowTitle(f"Detalhes do Orçamento - {budget.client.name}")
        self.resize(600, 500)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Informações do cliente
        client_group = QtWidgets.QGroupBox("Cliente")
        client_layout = QtWidgets.QFormLayout(client_group)
        client_layout.addRow("Nome:", QtWidgets.QLabel(self.budget.client.name))
        client_layout.addRow("Telefone:", QtWidgets.QLabel(self.budget.client.phone))
        if self.budget.client.email:
            client_layout.addRow("Email:", QtWidgets.QLabel(self.budget.client.email))
        layout.addWidget(client_group)
        
        # Produtos
        products_group = QtWidgets.QGroupBox("Produtos")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        self.products_list = QtWidgets.QListWidget()
        for item in self.budget.items:
            if item.product_type == "camiseta":
                text = f"Camiseta {item.fabric.title()} {item.sleeve.title()} {item.size} - Qtd: {item.quantity}"
            elif item.product_type == "conjunto":
                text = f"Conjunto {item.fabric.replace('_', ' ').title()} {item.sleeve.title()} - Qtd: {item.quantity}"
            elif item.product_type == "short":
                text = f"Short - Qtd: {item.quantity}"
            elif item.product_type == "comunicacao_visual":
                area = (item.width_cm or 0) * (item.height_cm or 0) / 10000
                text = f"{item.visual_type.title()} {item.width_cm}x{item.height_cm}cm ({area:.2f}m²)"
            elif item.product_type == "criacao_arte":
                text = f"Criação de Arte - R$ {item.art_creation_price:.2f}"
            else:
                text = f"Produto - Qtd: {item.quantity}"
            
            self.products_list.addItem(text)
        
        products_layout.addWidget(self.products_list)
        layout.addWidget(products_group)
        
        # Totais
        totals_group = QtWidgets.QGroupBox("Totais")
        totals_layout = QtWidgets.QFormLayout(totals_group)
        totals_layout.addRow("Subtotal:", QtWidgets.QLabel(f"R$ {self.budget.subtotal:.2f}"))
        if self.budget.art_creation_total > 0:
            totals_layout.addRow("Criação de Arte:", QtWidgets.QLabel(f"R$ {self.budget.art_creation_total:.2f}"))
        if self.budget.discount:
            totals_layout.addRow("Desconto:", QtWidgets.QLabel(f"R$ {self.budget.discount.value:.2f}"))
        totals_layout.addRow("Total:", QtWidgets.QLabel(f"R$ {self.budget.total:.2f}"))
        layout.addWidget(totals_group)
        
        # Botões
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
