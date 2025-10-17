from PyQt6 import QtWidgets, QtGui, QtCore
from decimal import Decimal
from datetime import date
import os

from ..core.simulator_models import (
    ProductType, FabricType, SleeveType, SizeType, VisualType, ClientType,
    ProductItem, ClientInfo, Discount, Budget, PriceDatabase
)
from ..core.budget_storage import BudgetStorage
from ..core.validators import BudgetValidator
from .budget_search_dialog import BudgetSearchDialog


class SimulatorWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Orçamentos - Manauara Design")
        self.resize(1000, 700)
        self.price_db = PriceDatabase()
        self.storage = BudgetStorage()
        self.validator = BudgetValidator()
        self.budget = Budget(
            client=ClientInfo(name="", phone=""),
            created_date=date.today().isoformat()
        )
        self._init_ui()

    def _init_ui(self):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)

        # Informações do Cliente
        client_group = QtWidgets.QGroupBox("Informações do Cliente")
        client_layout = QtWidgets.QGridLayout(client_group)
        
        client_layout.addWidget(QtWidgets.QLabel("Nome:"), 0, 0)
        self.client_name = QtWidgets.QLineEdit()
        self.client_name.setPlaceholderText("Nome completo do cliente")
        client_layout.addWidget(self.client_name, 0, 1, 1, 2)
        
        client_layout.addWidget(QtWidgets.QLabel("Telefone:"), 1, 0)
        self.client_phone = QtWidgets.QLineEdit()
        self.client_phone.setPlaceholderText("(11) 99999-9999")
        self.client_phone.textChanged.connect(self._format_phone)
        client_layout.addWidget(self.client_phone, 1, 1)
        
        client_layout.addWidget(QtWidgets.QLabel("Email:"), 1, 2)
        self.client_email = QtWidgets.QLineEdit()
        self.client_email.setPlaceholderText("email@exemplo.com")
        client_layout.addWidget(self.client_email, 1, 3)
        
        client_layout.addWidget(QtWidgets.QLabel("Tipo:"), 2, 0)
        self.client_type = QtWidgets.QComboBox()
        self.client_type.addItems(["Cliente Normal", "Terceirizado"])
        client_layout.addWidget(self.client_type, 2, 1)

        layout.addWidget(client_group)

        # Produtos
        products_group = QtWidgets.QGroupBox("Produtos")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        # Botão para adicionar produto
        add_product_btn = QtWidgets.QPushButton("+ Adicionar Produto")
        add_product_btn.clicked.connect(self._add_product_dialog)
        products_layout.addWidget(add_product_btn)
        
        # Lista de produtos
        self.products_list = QtWidgets.QListWidget()
        self.products_list.setMaximumHeight(200)
        products_layout.addWidget(self.products_list)
        
        # Botões para gerenciar produtos
        manage_products_layout = QtWidgets.QHBoxLayout()
        self.remove_product_btn = QtWidgets.QPushButton("Remover Selecionado")
        self.remove_product_btn.clicked.connect(self._remove_selected_product)
        self.remove_product_btn.setEnabled(False)
        manage_products_layout.addWidget(self.remove_product_btn)
        manage_products_layout.addStretch(1)
        products_layout.addLayout(manage_products_layout)
        
        # Conectar seleção para habilitar botão remover
        self.products_list.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(products_group)

        # Resumo do Orçamento
        summary_group = QtWidgets.QGroupBox("Resumo do Orçamento")
        summary_layout = QtWidgets.QGridLayout(summary_group)
        
        self.subtotal_label = QtWidgets.QLabel("Subtotal: R$ 0,00")
        self.art_creation_label = QtWidgets.QLabel("Criação de Arte: R$ 0,00")
        self.discount_label = QtWidgets.QLabel("Desconto: R$ 0,00")
        self.total_label = QtWidgets.QLabel("Total: R$ 0,00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        summary_layout.addWidget(self.subtotal_label, 0, 0)
        summary_layout.addWidget(self.art_creation_label, 1, 0)
        summary_layout.addWidget(self.discount_label, 2, 0)
        summary_layout.addWidget(self.total_label, 3, 0)
        
        # Desconto
        discount_layout = QtWidgets.QHBoxLayout()
        discount_layout.addWidget(QtWidgets.QLabel("Desconto:"))
        self.discount_type = QtWidgets.QComboBox()
        self.discount_type.addItems(["Sem desconto", "Percentual (%)", "Valor fixo (R$)"])
        self.discount_type.currentTextChanged.connect(self._on_discount_type_changed)
        discount_layout.addWidget(self.discount_type)
        
        self.discount_value = QtWidgets.QDoubleSpinBox()
        self.discount_value.setRange(0, 999999)
        self.discount_value.setDecimals(2)
        self.discount_value.setEnabled(False)
        self.discount_value.valueChanged.connect(self._calculate_totals)
        discount_layout.addWidget(self.discount_value)
        
        summary_layout.addLayout(discount_layout, 4, 0)

        layout.addWidget(summary_group)

        # Ações
        actions_layout = QtWidgets.QHBoxLayout()
        
        self.new_budget_btn = QtWidgets.QPushButton("Novo Orçamento")
        self.new_budget_btn.clicked.connect(self._new_budget)
        
        self.search_budgets_btn = QtWidgets.QPushButton("Buscar Orçamentos")
        self.search_budgets_btn.clicked.connect(self._search_budgets)
        
        self.save_budget_btn = QtWidgets.QPushButton("Salvar Orçamento")
        self.save_budget_btn.clicked.connect(self._save_budget)
        
        self.generate_pdf_btn = QtWidgets.QPushButton("Gerar PDF")
        self.generate_pdf_btn.clicked.connect(self._generate_pdf)
        
        actions_layout.addWidget(self.new_budget_btn)
        actions_layout.addWidget(self.search_budgets_btn)
        actions_layout.addWidget(self.save_budget_btn)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.generate_pdf_btn)

        layout.addLayout(actions_layout)

        self.setCentralWidget(container)

        # Ícone da aplicação
        try:
            from .start_window import load_app_icon
            app_icon = load_app_icon()
            if not app_icon.isNull():
                self.setWindowIcon(app_icon)
        except Exception:
            pass

    def _add_product_dialog(self):
        """Abre diálogo para adicionar produto"""
        dialog = ProductDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            product = dialog.get_product()
            if product:
                self.budget.items.append(product)
                self._update_products_list()
                self._calculate_totals()

    def _update_products_list(self):
        """Atualiza lista de produtos"""
        self.products_list.clear()
        for i, item in enumerate(self.budget.items):
            text = self._format_product_item(item)
            self.products_list.addItem(f"{i+1}. {text}")

    def _format_product_item(self, item: ProductItem) -> str:
        """Formata item do produto para exibição"""
        if item.product_type == "camiseta":
            return f"Camiseta {item.fabric} {item.sleeve} {item.size} - Qtd: {item.quantity}"
        elif item.product_type == "conjunto":
            return f"Conjunto {item.fabric} {item.sleeve} - Qtd: {item.quantity}"
        elif item.product_type == "short":
            return f"Short - Qtd: {item.quantity}"
        elif item.product_type == "comunicacao_visual":
            area = (item.width_cm or 0) * (item.height_cm or 0) / 10000  # cm² para m²
            return f"{item.visual_type} - {item.width_cm}x{item.height_cm}cm ({area:.2f}m²)"
        return f"Produto - Qtd: {item.quantity}"

    def _calculate_totals(self):
        """Calcula totais do orçamento"""
        subtotal = Decimal('0')
        art_creation_total = Decimal('0')
        
        for item in self.budget.items:
            item_price = self._calculate_item_price(item)
            subtotal += item_price * item.quantity
            
            if item.art_creation_price:
                art_creation_total += item.art_creation_price
        
        self.budget.subtotal = subtotal
        self.budget.art_creation_total = art_creation_total
        
        # Aplicar desconto
        discount_amount = Decimal('0')
        if self.discount_type.currentText() != "Sem desconto":
            if self.discount_type.currentText() == "Percentual (%)":
                discount_amount = subtotal * Decimal(str(self.discount_value.value())) / 100
            else:  # Valor fixo
                discount_amount = Decimal(str(self.discount_value.value()))
        
        self.budget.total = subtotal + art_creation_total - discount_amount
        
        # Atualizar labels
        self.subtotal_label.setText(f"Subtotal: R$ {subtotal:.2f}")
        self.art_creation_label.setText(f"Criação de Arte: R$ {art_creation_total:.2f}")
        self.discount_label.setText(f"Desconto: R$ {discount_amount:.2f}")
        self.total_label.setText(f"Total: R$ {self.budget.total:.2f}")

    def _calculate_item_price(self, item: ProductItem) -> Decimal:
        """Calcula preço de um item"""
        client_type = "terceiro" if self.client_type.currentText() == "Terceirizado" else "normal"
        
        if item.product_type == "camiseta":
            return self.price_db.get_camiseta_price(
                item.fabric, item.sleeve, item.size, client_type
            )
        elif item.product_type == "conjunto":
            conjunto_type = f"{item.fabric}_tactel"  # Simplificado
            return self.price_db.get_conjunto_price(conjunto_type, item.sleeve, client_type)
        elif item.product_type == "short":
            return self.price_db.get_short_price(client_type)
        elif item.product_type == "comunicacao_visual":
            area_m2 = (item.width_cm or 0) * (item.height_cm or 0) / 10000
            return self.price_db.get_visual_price(item.visual_type) * Decimal(str(area_m2))
        
        return Decimal('0')

    def _on_discount_type_changed(self):
        """Callback quando tipo de desconto muda"""
        self.discount_value.setEnabled(self.discount_type.currentText() != "Sem desconto")
        self._calculate_totals()

    def _new_budget(self):
        """Cria novo orçamento"""
        self.budget = Budget(
            client=ClientInfo(name="", phone=""),
            created_date=date.today().isoformat()
        )
        self.client_name.clear()
        self.client_phone.clear()
        self.client_email.clear()
        self.client_type.setCurrentIndex(0)
        self.products_list.clear()
        self.discount_type.setCurrentIndex(0)
        self.discount_value.setValue(0)
        self._calculate_totals()

    def _generate_pdf(self):
        """Gera PDF do orçamento"""
        # Atualizar dados do cliente
        self.budget.client.name = self.client_name.text().strip()
        self.budget.client.phone = self.client_phone.text().strip()
        self.budget.client.email = self.client_email.text().strip() or None
        
        # Validar orçamento
        is_valid, errors, warnings = self.validator.validate_budget(self.budget)
        
        if not is_valid:
            error_msg = "❌ ERROS ENCONTRADOS:\n\n" + "\n".join(f"• {error}" for error in errors)
            QtWidgets.QMessageBox.critical(self, "Orçamento Inválido", error_msg)
            return
        
        # Mostrar avisos se houver
        if warnings:
            warning_msg = "⚠️ AVISOS:\n\n" + "\n".join(f"• {warning}" for warning in warnings)
            warning_msg += "\n\nDeseja continuar mesmo assim?"
            reply = QtWidgets.QMessageBox.question(
                self, "Avisos", warning_msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return
        
        # Diálogo de confirmação com opção WhatsApp
        confirmation = BudgetConfirmationDialog(self.budget, self)
        if confirmation.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            if confirmation.should_generate_pdf:
                self._generate_pdf_file()
            if confirmation.should_send_whatsapp:
                self._send_whatsapp()
    
    def _generate_pdf_file(self):
        """Gera arquivo PDF"""
        default_name = f"Orcamento_{self.budget.client.name}_{date.today().isoformat()}.pdf"
        settings = QtCore.QSettings("ManauaraDesign", "BudgetApp")
        start_dir = settings.value("lastDir", os.getcwd())
        initial_path = os.path.join(start_dir, default_name)
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Salvar Orçamento", initial_path, "PDF (*.pdf)"
        )
        if not path:
            return
        
        settings.setValue("lastDir", os.path.dirname(path))
        
        try:
            from ..pdf.budget_generator import BudgetPDF
            pdf = BudgetPDF()
            pdf.generate(self.budget, path)
            QtWidgets.QMessageBox.information(self, "Sucesso", "Orçamento gerado com sucesso.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {str(e)}")
    
    def _send_whatsapp(self):
        """Abre WhatsApp Web com mensagem pré-formatada"""
        # Remove todos os caracteres não numéricos
        phone = ''.join(filter(str.isdigit, self.budget.client.phone))
        
        # Se tem 11 dígitos (DDD + 9 dígitos), remove o DDD
        if len(phone) == 11:
            phone = phone[2:]  # Remove os 2 primeiros dígitos (DDD)
        # Se tem 10 dígitos (DDD + 8 dígitos), remove o DDD
        elif len(phone) == 10:
            phone = phone[2:]  # Remove os 2 primeiros dígitos (DDD)
        # Se tem 9 dígitos, já está no formato correto
        elif len(phone) == 9:
            pass  # Já está correto
        # Se tem 8 dígitos, adiciona o 9
        elif len(phone) == 8:
            phone = "9" + phone
        
        message = f"""Olá {self.budget.client.name}! 👋

Aqui está seu orçamento da Manauara Design:

📋 *Resumo do Orçamento:*
• Total: R$ {self.budget.total:.2f}
• {len(self.budget.items)} item(ns) no orçamento

💡 *Como posso ajudar:*
• Dúvidas sobre produtos ou especificações
• Ajustes de quantidades ou tamanhos  
• Informações sobre prazos de entrega
• Negociação de descontos especiais

Estou à disposição para esclarecer qualquer dúvida! 😊

_Manauara Design_"""
        
        # Codificar mensagem para URL
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{phone}?&text={encoded_message}"
        import webbrowser
        webbrowser.open(whatsapp_url)
    
    def _search_budgets(self):
        """Abre diálogo de busca de orçamentos"""
        dialog = BudgetSearchDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selected_budget = dialog.get_selected_budget()
            if selected_budget:
                self._load_budget(selected_budget)
    
    def _load_budget(self, budget: Budget):
        """Carrega um orçamento na interface"""
        # Limpar interface atual
        self._new_budget()
        
        # Carregar dados do cliente
        self.client_name.setText(budget.client.name)
        self.client_phone.setText(budget.client.phone)
        self.client_email.setText(budget.client.email or "")
        
        # Carregar produtos
        self.budget = budget
        self._update_products_list()
        self._calculate_totals()
        
        QtWidgets.QMessageBox.information(self, "Sucesso", "Orçamento carregado com sucesso!")
    
    def _save_budget(self):
        """Salva orçamento atual"""
        # Atualizar dados do cliente
        self.budget.client.name = self.client_name.text().strip()
        self.budget.client.phone = self.client_phone.text().strip()
        self.budget.client.email = self.client_email.text().strip() or None
        
        # Validar antes de salvar
        is_valid, errors, warnings = self.validator.validate_budget(self.budget)
        
        if not is_valid:
            error_msg = "❌ ERROS ENCONTRADOS:\n\n" + "\n".join(f"• {error}" for error in errors)
            QtWidgets.QMessageBox.critical(self, "Orçamento Inválido", error_msg)
            return
        
        try:
            budget_id = self.storage.save_budget(self.budget)
            QtWidgets.QMessageBox.information(
                self, "Sucesso", 
                f"Orçamento salvo com sucesso!\nID: {budget_id}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar orçamento: {str(e)}")

    def _format_phone(self):
        """Formata telefone automaticamente"""
        text = self.client_phone.text()
        # Remove caracteres não numéricos
        numbers = ''.join(filter(str.isdigit, text))
        
        if len(numbers) <= 11:
            if len(numbers) >= 2:
                formatted = f"({numbers[:2]})"
                if len(numbers) > 2:
                    formatted += f" {numbers[2]}"
                if len(numbers) > 3:
                    formatted += f" {numbers[3:7]}"
                if len(numbers) > 7:
                    formatted += f"-{numbers[7:]}"
                
                # Evita loop infinito
                if formatted != text:
                    self.client_phone.blockSignals(True)
                    self.client_phone.setText(formatted)
                    self.client_phone.blockSignals(False)

    def _on_selection_changed(self):
        """Habilita/desabilita botão remover baseado na seleção"""
        has_selection = len(self.products_list.selectedItems()) > 0
        self.remove_product_btn.setEnabled(has_selection)

    def _remove_selected_product(self):
        """Remove produto selecionado da lista"""
        current_row = self.products_list.currentRow()
        if current_row >= 0 and current_row < len(self.budget.items):
            del self.budget.items[current_row]
            self._update_products_list()
            self._calculate_totals()


class ProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Produto")
        self.setModal(True)
        self.resize(400, 300)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Tipo de produto
        layout.addWidget(QtWidgets.QLabel("Tipo de Produto:"))
        self.product_type = QtWidgets.QComboBox()
        self.product_type.addItems(["Camiseta", "Conjunto", "Short", "Comunicação Visual", "Criação de Arte"])
        self.product_type.currentTextChanged.connect(self._on_product_type_changed)
        layout.addWidget(self.product_type)
        
        # Container para configurações específicas
        self.config_container = QtWidgets.QWidget()
        self.config_layout = QtWidgets.QVBoxLayout(self.config_container)
        layout.addWidget(self.config_container)
        
        # Quantidade
        layout.addWidget(QtWidgets.QLabel("Quantidade:"))
        self.quantity = QtWidgets.QSpinBox()
        self.quantity.setRange(1, 9999)
        self.quantity.setValue(1)
        layout.addWidget(self.quantity)
        
        # Criação de arte removida - agora é produto separado
        
        # Botões
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | 
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self._on_product_type_changed()

    def _on_product_type_changed(self):
        """Atualiza interface baseada no tipo de produto"""
        # Limpar configurações anteriores
        for i in reversed(range(self.config_layout.count())):
            self.config_layout.itemAt(i).widget().setParent(None)
        
        product_type = self.product_type.currentText()
        
        if product_type == "Camiseta":
            self._setup_camiseta_config()
        elif product_type == "Conjunto":
            self._setup_conjunto_config()
        elif product_type == "Short":
            self._setup_short_config()
        elif product_type == "Comunicação Visual":
            self._setup_visual_config()
        elif product_type == "Criação de Arte":
            self._setup_art_config()

    def _setup_camiseta_config(self):
        """Configuração para camisetas"""
        # Tecido
        self.config_layout.addWidget(QtWidgets.QLabel("Tecido:"))
        self.fabric = QtWidgets.QComboBox()
        self.fabric.addItems(["Dryfit", "Helanca"])
        self.config_layout.addWidget(self.fabric)
        
        # Manga
        self.config_layout.addWidget(QtWidgets.QLabel("Manga:"))
        self.sleeve = QtWidgets.QComboBox()
        self.sleeve.addItems(["Curta", "Longa"])
        self.config_layout.addWidget(self.sleeve)
        
        # Tamanho
        self.config_layout.addWidget(QtWidgets.QLabel("Tamanho:"))
        self.size = QtWidgets.QComboBox()
        self.size.addItems(["PP", "P", "M", "G", "GG", "XG", "XGG", "XG3", "2", "4", "6", "8", "10", "12", "14", "16"])
        self.config_layout.addWidget(self.size)

    def _setup_conjunto_config(self):
        """Configuração para conjuntos"""
        # Tipo de conjunto
        self.config_layout.addWidget(QtWidgets.QLabel("Tipo de Conjunto:"))
        self.conjunto_type = QtWidgets.QComboBox()
        self.conjunto_type.addItems(["Helanca + Tactel", "Todo Helanca", "Dryfit + Helanca"])
        self.config_layout.addWidget(self.conjunto_type)
        
        # Manga
        self.config_layout.addWidget(QtWidgets.QLabel("Manga:"))
        self.sleeve = QtWidgets.QComboBox()
        self.sleeve.addItems(["Curta", "Longa"])
        self.config_layout.addWidget(self.sleeve)

    def _setup_short_config(self):
        """Configuração para shorts"""
        self.config_layout.addWidget(QtWidgets.QLabel("Short - Preço base: R$ 25,00"))

    def _setup_visual_config(self):
        """Configuração para comunicação visual"""
        # Tipo
        self.config_layout.addWidget(QtWidgets.QLabel("Tipo:"))
        self.visual_type = QtWidgets.QComboBox()
        self.visual_type.addItems(["Lona", "Adesivo", "Adesivo Perfurado", "Banner"])
        self.config_layout.addWidget(self.visual_type)
        
        # Dimensões
        dims_layout = QtWidgets.QHBoxLayout()
        dims_layout.addWidget(QtWidgets.QLabel("Largura (cm):"))
        self.width = QtWidgets.QDoubleSpinBox()
        self.width.setRange(0.1, 9999)
        self.width.setDecimals(1)
        dims_layout.addWidget(self.width)
        
        dims_layout.addWidget(QtWidgets.QLabel("Altura (cm):"))
        self.height = QtWidgets.QDoubleSpinBox()
        self.height.setRange(0.1, 9999)
        self.height.setDecimals(1)
        dims_layout.addWidget(self.height)
        
        self.config_layout.addLayout(dims_layout)

    def _setup_art_config(self):
        """Configuração para criação de arte"""
        self.config_layout.addWidget(QtWidgets.QLabel("Criação de Arte - Valor personalizado"))
        
        # Valor da arte
        self.config_layout.addWidget(QtWidgets.QLabel("Valor (R$):"))
        self.art_value = QtWidgets.QDoubleSpinBox()
        self.art_value.setRange(0, 9999)
        self.art_value.setDecimals(2)
        self.art_value.setSuffix(" R$")
        self.config_layout.addWidget(self.art_value)

    def get_product(self) -> ProductItem:
        """Retorna produto configurado"""
        product_type_map = {
            "Camiseta": "camiseta",
            "Conjunto": "conjunto", 
            "Short": "short",
            "Comunicação Visual": "comunicacao_visual",
            "Criação de Arte": "criacao_arte"
        }
        
        item = ProductItem(
            product_type=product_type_map[self.product_type.currentText()],
            quantity=self.quantity.value()
        )
        
        # Criação de arte agora é produto separado
        
        if self.product_type.currentText() == "Camiseta":
            item.fabric = self.fabric.currentText().lower()
            item.sleeve = self.sleeve.currentText().lower()
            item.size = self.size.currentText()
            
        elif self.product_type.currentText() == "Conjunto":
            item.sleeve = self.sleeve.currentText().lower()
            # Mapear tipo de conjunto
            conjunto_map = {
                "Helanca + Tactel": "helanca_tactel",
                "Todo Helanca": "todo_helanca", 
                "Dryfit + Helanca": "dryfit_helanca"
            }
            item.fabric = conjunto_map[self.conjunto_type.currentText()]
            
        elif self.product_type.currentText() == "Comunicação Visual":
            visual_map = {
                "Lona": "lona",
                "Adesivo": "adesivo",
                "Adesivo Perfurado": "adesivo_perfurado",
                "Banner": "banner"
            }
            item.visual_type = visual_map[self.visual_type.currentText()]
            item.width_cm = self.width.value()
            item.height_cm = self.height.value()
        elif self.product_type.currentText() == "Criação de Arte":
            item.art_creation_price = Decimal(str(self.art_value.value()))
        
        return item


class BudgetConfirmationDialog(QtWidgets.QDialog):
    def __init__(self, budget: Budget, parent=None):
        super().__init__(parent)
        self.budget = budget
        self.should_generate_pdf = False
        self.should_send_whatsapp = False
        self.setWindowTitle("Confirmar Geração do Orçamento")
        self.resize(500, 400)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Título
        title = QtWidgets.QLabel("📋 Confirmação do Orçamento")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Resumo do orçamento
        summary_group = QtWidgets.QGroupBox("Resumo")
        summary_layout = QtWidgets.QFormLayout(summary_group)
        
        summary_layout.addRow("Cliente:", QtWidgets.QLabel(self.budget.client.name))
        summary_layout.addRow("Telefone:", QtWidgets.QLabel(self.budget.client.phone))
        summary_layout.addRow("Total:", QtWidgets.QLabel(f"R$ {self.budget.total:.2f}"))
        summary_layout.addRow("Itens:", QtWidgets.QLabel(f"{len(self.budget.items)} produto(s)"))
        
        layout.addWidget(summary_group)
        
        # Opções de ação
        actions_group = QtWidgets.QGroupBox("O que deseja fazer?")
        actions_layout = QtWidgets.QVBoxLayout(actions_group)
        
        # Gerar PDF
        self.generate_pdf_cb = QtWidgets.QCheckBox("📄 Gerar arquivo PDF do orçamento")
        self.generate_pdf_cb.setChecked(True)
        actions_layout.addWidget(self.generate_pdf_cb)
        
        # Enviar WhatsApp
        self.send_whatsapp_cb = QtWidgets.QCheckBox("📱 Enviar via WhatsApp Web")
        self.send_whatsapp_cb.setChecked(True)
        actions_layout.addWidget(self.send_whatsapp_cb)
        
        # Informações sobre WhatsApp
        whatsapp_info = QtWidgets.QLabel(
            "• Abrirá o WhatsApp Web automaticamente\n"
            "• Mensagem pré-formatada com resumo do orçamento\n"
            "• Inclui sugestões de como o cliente pode te ajudar"
        )
        whatsapp_info.setStyleSheet("color: gray; font-size: 11px; margin-left: 20px;")
        actions_layout.addWidget(whatsapp_info)
        
        layout.addWidget(actions_group)
        
        # Botões
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | 
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_ok(self):
        """Confirma ações selecionadas"""
        self.should_generate_pdf = self.generate_pdf_cb.isChecked()
        self.should_send_whatsapp = self.send_whatsapp_cb.isChecked()
        
        if not self.should_generate_pdf and not self.should_send_whatsapp:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma opção.")
            return
        
        self.accept()
