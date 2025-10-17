from PyQt6 import QtWidgets, QtGui, QtCore
from decimal import Decimal
import json
import os
from typing import Dict, List

from ..core.simulator_models import PriceDatabase
from .theme import ThemeManager


class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administração - Manauara Design")
        self.resize(1000, 700)
        self.price_db = PriceDatabase()
        self._init_ui()
        self._init_menu()
        self._load_prices()

    def _init_ui(self):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)

        toolbar = QtWidgets.QToolBar("Principal", self)
        toolbar.setMovable(False)
        # Aplica o estilo verde aos botões da toolbar
        toolbar.setStyleSheet("""
            QToolButton {
                background-color: #4CAF50;   /* verde */
                color: white;                /* texto branco */
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }

            QToolButton:hover {
                background-color: #45a049;   /* verde mais escuro ao passar o mouse */
            }

            QToolButton:pressed {
                background-color: #3e8e41;   /* verde ainda mais escuro ao clicar */
            }
        """)

        action_home = QtGui.QAction("Voltar ao Início", self)
        action_home.triggered.connect(self._go_back_to_start)

        toolbar.addAction(action_home)
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, toolbar)

        # Título
        title = QtWidgets.QLabel("⚙️ Administração do Sistema")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Abas
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Aba de Preços
        self.prices_tab = self._create_prices_tab()
        self.tab_widget.addTab(self.prices_tab, "💰 Preços")
        
        # Aba de Produtos
        self.products_tab = self._create_products_tab()
        self.tab_widget.addTab(self.products_tab, "📦 Produtos")
        
        # Aba de Configurações
        self.settings_tab = self._create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Configurações")
        
        layout.addWidget(self.tab_widget)

        # Botões de ação
        actions_layout = QtWidgets.QHBoxLayout()
        
        self.save_btn = QtWidgets.QPushButton("💾 Salvar Alterações")
        self.save_btn.clicked.connect(self._save_all_changes)
        
        self.reload_btn = QtWidgets.QPushButton("🔄 Recarregar")
        self.reload_btn.clicked.connect(self._reload_data)
        
        self.backup_btn = QtWidgets.QPushButton("📁 Backup")
        self.backup_btn.clicked.connect(self._create_backup)
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.reload_btn)
        actions_layout.addWidget(self.backup_btn)
        actions_layout.addStretch(1)
        
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

    def _init_menu(self):
        bar = self.menuBar()
        app_menu = bar.addMenu("Aplicativo")

        action_toggle_theme = QtGui.QAction("Alternar tema (Claro/Escuro)", self)
        action_toggle_theme.triggered.connect(self._toggle_theme)
        app_menu.addAction(action_toggle_theme)

        action_back = QtGui.QAction("Voltar ao Início", self)
        action_back.triggered.connect(self._go_back_to_start)
        app_menu.addAction(action_back)

    def _toggle_theme(self):
        app = QtWidgets.QApplication.instance()
        if app is not None:
            ThemeManager.toggle_theme(app)

    def _go_back_to_start(self):
        from .start_window import StartDialog
        dlg = StartDialog(None)
        self.hide()
        result = dlg.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            if dlg.start_ficha:
                from .main_window import MainWindow
                win = MainWindow()
                win.show()
                self._next_window = win
            elif dlg.start_orcamento:
                from .simulator_window import SimulatorWindow
                win = SimulatorWindow()
                win.show()
                self._next_window = win
            elif dlg.start_admin:
                win = AdminWindow()
                win.show()
                self._next_window = win
            self.close()
        else:
            # Usuário cancelou: manter janela atual
            self.show()

    def _create_prices_tab(self):
        """Cria aba de preços"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # Preços de Camisetas
        camisetas_group = QtWidgets.QGroupBox("Preços de Camisetas")
        camisetas_layout = QtWidgets.QVBoxLayout(camisetas_group)
        
        # Tabela de preços
        self.prices_table = QtWidgets.QTableWidget()
        self.prices_table.setColumnCount(4)
        self.prices_table.setHorizontalHeaderLabels(["Tecido", "Manga", "Tamanho", "Preço (R$)"])
        self.prices_table.horizontalHeader().setStretchLastSection(True)
        camisetas_layout.addWidget(self.prices_table)
        
        # Botões para camisetas
        camisetas_buttons = QtWidgets.QHBoxLayout()
        self.add_price_btn = QtWidgets.QPushButton("+ Adicionar Preço")
        self.add_price_btn.clicked.connect(self._add_price)
        self.remove_price_btn = QtWidgets.QPushButton("- Remover Selecionado")
        self.remove_price_btn.clicked.connect(self._remove_price)
        self.remove_price_btn.setEnabled(False)
        camisetas_buttons.addWidget(self.add_price_btn)
        camisetas_buttons.addWidget(self.remove_price_btn)
        camisetas_buttons.addStretch(1)
        camisetas_layout.addLayout(camisetas_buttons)
        
        layout.addWidget(camisetas_group)
        
        # Preços de Comunicação Visual
        visual_group = QtWidgets.QGroupBox("Preços de Comunicação Visual")
        visual_layout = QtWidgets.QVBoxLayout(visual_group)
        self.visual_table = QtWidgets.QTableWidget()
        self.visual_table.setColumnCount(3)
        self.visual_table.setHorizontalHeaderLabels(["Produto", "Preço (R$)", "Por m²"])
        self.visual_table.horizontalHeader().setStretchLastSection(True)
        visual_layout.addWidget(self.visual_table)
        vb = QtWidgets.QHBoxLayout()
        self.btn_visual_add = QtWidgets.QPushButton("+ Adicionar")
        self.btn_visual_edit = QtWidgets.QPushButton("✏️ Editar")
        self.btn_visual_remove = QtWidgets.QPushButton("- Remover")
        self.btn_visual_edit.setEnabled(False)
        self.btn_visual_remove.setEnabled(False)
        self.btn_visual_add.clicked.connect(self._on_visual_add)
        self.btn_visual_edit.clicked.connect(self._on_visual_edit)
        self.btn_visual_remove.clicked.connect(self._on_visual_remove)
        vb.addWidget(self.btn_visual_add)
        vb.addWidget(self.btn_visual_edit)
        vb.addWidget(self.btn_visual_remove)
        vb.addStretch(1)
        visual_layout.addLayout(vb)
        layout.addWidget(visual_group)
        
        # Outros preços
        others_group = QtWidgets.QGroupBox("Outros Preços")
        others_layout = QtWidgets.QVBoxLayout(others_group)
        self.others_table = QtWidgets.QTableWidget()
        self.others_table.setColumnCount(3)
        self.others_table.setHorizontalHeaderLabels(["Produto", "Preço (R$)", "Por m²"])
        self.others_table.horizontalHeader().setStretchLastSection(True)
        others_layout.addWidget(self.others_table)
        ob = QtWidgets.QHBoxLayout()
        self.btn_others_add = QtWidgets.QPushButton("+ Adicionar")
        self.btn_others_edit = QtWidgets.QPushButton("✏️ Editar")
        self.btn_others_remove = QtWidgets.QPushButton("- Remover")
        self.btn_others_edit.setEnabled(False)
        self.btn_others_remove.setEnabled(False)
        self.btn_others_add.clicked.connect(self._on_others_add)
        self.btn_others_edit.clicked.connect(self._on_others_edit)
        self.btn_others_remove.clicked.connect(self._on_others_remove)
        ob.addWidget(self.btn_others_add)
        ob.addWidget(self.btn_others_edit)
        ob.addWidget(self.btn_others_remove)
        ob.addStretch(1)
        others_layout.addLayout(ob)
        layout.addWidget(others_group)
        
        # Conectar seleção da tabela
        self.prices_table.itemSelectionChanged.connect(self._on_price_selection_changed)
        
        return tab

    def _create_products_tab(self):
        """Cria aba de produtos"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # Lista de produtos
        products_group = QtWidgets.QGroupBox("Produtos Disponíveis")
        products_layout = QtWidgets.QVBoxLayout(products_group)
        
        self.products_list = QtWidgets.QListWidget()
        products_layout.addWidget(self.products_list)
        
        # Botões de produtos
        products_buttons = QtWidgets.QHBoxLayout()
        self.add_product_btn = QtWidgets.QPushButton("+ Adicionar Produto")
        self.add_product_btn.clicked.connect(self._add_product)
        self.edit_product_btn = QtWidgets.QPushButton("✏️ Editar")
        self.edit_product_btn.clicked.connect(self._edit_product)
        self.edit_product_btn.setEnabled(False)
        self.remove_product_btn = QtWidgets.QPushButton("- Remover")
        self.remove_product_btn.clicked.connect(self._remove_product)
        self.remove_product_btn.setEnabled(False)
        products_buttons.addWidget(self.add_product_btn)
        products_buttons.addWidget(self.edit_product_btn)
        products_buttons.addWidget(self.remove_product_btn)
        products_buttons.addStretch(1)
        products_layout.addLayout(products_buttons)
        
        layout.addWidget(products_group)
        
        # Conectar seleção
        self.products_list.itemSelectionChanged.connect(self._on_product_selection_changed)
        
        return tab

    def _create_settings_tab(self):
        """Cria aba de configurações"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # Configurações gerais
        general_group = QtWidgets.QGroupBox("Configurações Gerais")
        general_layout = QtWidgets.QFormLayout(general_group)
        
        self.min_quantity_camiseta = QtWidgets.QSpinBox()
        self.min_quantity_camiseta.setRange(1, 999)
        general_layout.addRow("Quantidade mínima - Camisetas:", self.min_quantity_camiseta)
        
        self.min_quantity_conjunto = QtWidgets.QSpinBox()
        self.min_quantity_conjunto.setRange(1, 999)
        general_layout.addRow("Quantidade mínima - Conjuntos:", self.min_quantity_conjunto)
        
        self.min_quantity_short = QtWidgets.QSpinBox()
        self.min_quantity_short.setRange(1, 999)
        general_layout.addRow("Quantidade mínima - Shorts:", self.min_quantity_short)
        
        layout.addWidget(general_group)
        
        # Configurações de WhatsApp
        whatsapp_group = QtWidgets.QGroupBox("Configurações do WhatsApp")
        whatsapp_layout = QtWidgets.QFormLayout(whatsapp_group)
        
        self.whatsapp_message = QtWidgets.QPlainTextEdit()
        self.whatsapp_message.setMaximumHeight(150)
        whatsapp_layout.addRow("Mensagem padrão:", self.whatsapp_message)
        
        layout.addWidget(whatsapp_group)
        
        # Configurações de PDF
        pdf_group = QtWidgets.QGroupBox("Configurações do PDF")
        pdf_layout = QtWidgets.QFormLayout(pdf_group)
        
        self.pdf_footer = QtWidgets.QLineEdit()
        pdf_layout.addRow("Rodapé do PDF:", self.pdf_footer)
        
        layout.addWidget(pdf_group)
        
        return tab

    def _load_prices(self):
        """Carrega preços na interface"""
        # Carregar preços de camisetas na tabela
        self._populate_prices_table()

        # Tentar carregar de config/prices.json
        config_path = os.path.join("config", "prices.json")
        visual_data = []
        others_data = []
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    visual_data = [(v.get("nome", ""), f"{v.get('preco_m2', 0):.2f}", True) for v in data.get("visual", [])]
                    others_data = [(o.get("nome", ""), f"{o.get('preco', 0):.2f}", bool(o.get("por_m2", False))) for o in data.get("outros", [])]
            except Exception:
                visual_data = []
                others_data = []
        if not visual_data:
            visual_data = [("Lona", "60.00", True), ("Adesivo", "50.00", True), ("Adesivo Perfurado", "70.00", True), ("Banner", "50.00", True)]
        if not others_data:
            others_data = [("Short", "25.00", False)]

        self.visual_table.setRowCount(len(visual_data))
        for r, (name, price, por_m2) in enumerate(visual_data):
            self.visual_table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
            self.visual_table.setItem(r, 1, QtWidgets.QTableWidgetItem(price))
            self.visual_table.setItem(r, 2, QtWidgets.QTableWidgetItem("Sim" if por_m2 else "Não"))

        self.others_table.setRowCount(len(others_data))
        for r, (name, price, por_m2) in enumerate(others_data):
            self.others_table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
            self.others_table.setItem(r, 1, QtWidgets.QTableWidgetItem(price))
            self.others_table.setItem(r, 2, QtWidgets.QTableWidgetItem("Sim" if por_m2 else "Não"))
        
        # Carregar configurações
        self.min_quantity_camiseta.setValue(5)
        self.min_quantity_conjunto.setValue(1)
        self.min_quantity_short.setValue(1)
        
        # Carregar mensagem padrão do WhatsApp
        default_message = """Olá {nome}! 👋

Aqui está seu orçamento da Manauara Design:

📋 *Resumo do Orçamento:*
• Total: R$ {total}
• {itens} item(ns) no orçamento

💡 *Como posso ajudar:*
• Dúvidas sobre produtos ou especificações
• Ajustes de quantidades ou tamanhos  
• Informações sobre prazos de entrega
• Negociação de descontos especiais

Estou à disposição para esclarecer qualquer dúvida! 😊

_Manauara Design_"""
        self.whatsapp_message.setPlainText(default_message)
        
        # Carregar rodapé do PDF
        self.pdf_footer.setText("manauaradesig@gmail.com - Desenvolvido por Manauara Design - Todos os direitos reservados @2026")

        # Seleção habilita botões
        self.visual_table.itemSelectionChanged.connect(lambda: self._toggle_visual_actions())
        self.others_table.itemSelectionChanged.connect(lambda: self._toggle_others_actions())

    def _populate_prices_table(self):
        """Preenche tabela de preços"""
        # Dados de exemplo - em produção, carregaria do arquivo de configuração
        prices_data = [
            ("Dryfit", "Curta", "PP", "40.00"),
            ("Dryfit", "Curta", "P", "40.00"),
            ("Dryfit", "Curta", "M", "40.00"),
            ("Dryfit", "Curta", "G", "40.00"),
            ("Dryfit", "Curta", "GG", "45.00"),
            ("Dryfit", "Curta", "XG", "45.00"),
            ("Dryfit", "Longa", "PP", "45.00"),
            ("Dryfit", "Longa", "P", "45.00"),
            ("Dryfit", "Longa", "M", "45.00"),
            ("Dryfit", "Longa", "G", "45.00"),
            ("Dryfit", "Longa", "GG", "50.00"),
            ("Dryfit", "Longa", "XG", "53.00"),
            ("Helanca", "Curta", "PP", "35.00"),
            ("Helanca", "Curta", "P", "35.00"),
            ("Helanca", "Curta", "M", "35.00"),
            ("Helanca", "Curta", "G", "35.00"),
            ("Helanca", "Curta", "GG", "40.00"),
            ("Helanca", "Curta", "XG", "40.00"),
            ("Helanca", "Longa", "PP", "40.00"),
            ("Helanca", "Longa", "P", "40.00"),
            ("Helanca", "Longa", "M", "40.00"),
            ("Helanca", "Longa", "G", "40.00"),
            ("Helanca", "Longa", "GG", "45.00"),
            ("Helanca", "Longa", "XG", "48.00"),
        ]
        
        self.prices_table.setRowCount(len(prices_data))
        for row, (tecido, manga, tamanho, preco) in enumerate(prices_data):
            self.prices_table.setItem(row, 0, QtWidgets.QTableWidgetItem(tecido))
            self.prices_table.setItem(row, 1, QtWidgets.QTableWidgetItem(manga))
            self.prices_table.setItem(row, 2, QtWidgets.QTableWidgetItem(tamanho))
            self.prices_table.setItem(row, 3, QtWidgets.QTableWidgetItem(preco))
        
        self.prices_table.resizeColumnsToContents()

    def _on_price_selection_changed(self):
        """Habilita/desabilita botão remover preço"""
        has_selection = len(self.prices_table.selectedItems()) > 0
        self.remove_price_btn.setEnabled(has_selection)

    def _on_product_selection_changed(self):
        """Habilita/desabilita botões de produto"""
        has_selection = len(self.products_list.selectedItems()) > 0
        self.edit_product_btn.setEnabled(has_selection)
        self.remove_product_btn.setEnabled(has_selection)

    def _add_price(self):
        """Adiciona novo preço"""
        dialog = PriceDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            tecido, manga, tamanho, preco = dialog.get_data()
            row = self.prices_table.rowCount()
            self.prices_table.insertRow(row)
            self.prices_table.setItem(row, 0, QtWidgets.QTableWidgetItem(tecido))
            self.prices_table.setItem(row, 1, QtWidgets.QTableWidgetItem(manga))
            self.prices_table.setItem(row, 2, QtWidgets.QTableWidgetItem(tamanho))
            self.prices_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(preco)))

    def _remove_price(self):
        """Remove preço selecionado"""
        current_row = self.prices_table.currentRow()
        if current_row >= 0:
            self.prices_table.removeRow(current_row)

    def _add_product(self):
        """Adiciona novo produto"""
        dialog = ProductDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            product_name = dialog.get_product_name()
            self.products_list.addItem(product_name)

    def _edit_product(self):
        """Edita produto selecionado"""
        current_item = self.products_list.currentItem()
        if current_item:
            dialog = ProductDialog(self, current_item.text())
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                current_item.setText(dialog.get_product_name())

    def _remove_product(self):
        """Remove produto selecionado"""
        current_row = self.products_list.currentRow()
        if current_row >= 0:
            self.products_list.takeItem(current_row)

    def _save_all_changes(self):
        """Salva todas as alterações"""
        try:
            # Salvar preços
            self._save_prices()
            
            # Salvar configurações
            self._save_settings()
            
            QtWidgets.QMessageBox.information(self, "Sucesso", "Alterações salvas com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao salvar: {str(e)}")

    def _save_prices(self):
        """Salva preços em arquivo de configuração"""
        config = {
            "camisetas": [],
            "visual": [],
            "outros": [],
        }
        
        # Salvar preços de camisetas
        for row in range(self.prices_table.rowCount()):
            tecido = self.prices_table.item(row, 0).text()
            manga = self.prices_table.item(row, 1).text()
            tamanho = self.prices_table.item(row, 2).text()
            preco = float(self.prices_table.item(row, 3).text())
            
            config["camisetas"].append({
                "tecido": tecido.lower(),
                "manga": manga.lower(),
                "tamanho": tamanho,
                "preco": preco
            })
        
        # Visual
        for row in range(self.visual_table.rowCount()):
            name_item = self.visual_table.item(row, 0)
            price_item = self.visual_table.item(row, 1)
            m2_item = self.visual_table.item(row, 2)
            if not name_item or not price_item:
                continue
            config["visual"].append({
                "nome": name_item.text(),
                "preco_m2": float(price_item.text() or 0),
            })

        # Outros
        for row in range(self.others_table.rowCount()):
            name_item = self.others_table.item(row, 0)
            price_item = self.others_table.item(row, 1)
            m2_item = self.others_table.item(row, 2)
            if not name_item or not price_item:
                continue
            config["outros"].append({
                "nome": name_item.text(),
                "preco": float(price_item.text() or 0),
                "por_m2": (m2_item.text().strip().lower() == "sim") if m2_item else False,
            })

        # Salvar arquivo
        os.makedirs("config", exist_ok=True)
        with open("config/prices.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _save_settings(self):
        """Salva configurações"""
        config = {
            "quantidades_minimas": {
                "camiseta": self.min_quantity_camiseta.value(),
                "conjunto": self.min_quantity_conjunto.value(),
                "short": self.min_quantity_short.value()
            },
            "whatsapp": {
                "mensagem": self.whatsapp_message.toPlainText()
            },
            "pdf": {
                "rodape": self.pdf_footer.text()
            }
        }
        
        os.makedirs("config", exist_ok=True)
        with open("config/settings.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _reload_data(self):
        """Recarrega dados"""
        self._load_prices()
        QtWidgets.QMessageBox.information(self, "Sucesso", "Dados recarregados!")

    def _create_backup(self):
        """Cria backup das configurações"""
        import shutil
        from datetime import datetime
        
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copiar arquivos de configuração
        if os.path.exists("config"):
            shutil.copytree("config", f"{backup_dir}/config")
        
        if os.path.exists("data"):
            shutil.copytree("data", f"{backup_dir}/data")
        
        QtWidgets.QMessageBox.information(self, "Sucesso", f"Backup criado em: {backup_dir}")

    def _toggle_visual_actions(self):
        has = len(self.visual_table.selectedItems()) > 0
        self.btn_visual_edit.setEnabled(has)
        self.btn_visual_remove.setEnabled(has)

    def _toggle_others_actions(self):
        has = len(self.others_table.selectedItems()) > 0
        self.btn_others_edit.setEnabled(has)
        self.btn_others_remove.setEnabled(has)

    def _on_visual_add(self):
        dlg = ProductPriceDialog(self, title="Novo produto de comunicação visual", default_per_m2=True)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, price, per_m2 = dlg.get_values()
            r = self.visual_table.rowCount()
            self.visual_table.insertRow(r)
            self.visual_table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
            self.visual_table.setItem(r, 1, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            self.visual_table.setItem(r, 2, QtWidgets.QTableWidgetItem("Sim" if per_m2 else "Não"))

    def _on_visual_edit(self):
        r = self.visual_table.currentRow()
        if r < 0:
            return
        name = self.visual_table.item(r, 0).text()
        price = float(self.visual_table.item(r, 1).text() or 0)
        per_m2 = (self.visual_table.item(r, 2).text().strip().lower() == "sim")
        dlg = ProductPriceDialog(self, title="Editar produto de comunicação visual", default_name=name, default_price=price, default_per_m2=per_m2)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, price, per_m2 = dlg.get_values()
            self.visual_table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
            self.visual_table.setItem(r, 1, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            self.visual_table.setItem(r, 2, QtWidgets.QTableWidgetItem("Sim" if per_m2 else "Não"))

    def _on_visual_remove(self):
        self._table_remove_current(self.visual_table)

    def _on_others_add(self):
        dlg = ProductPriceDialog(self, title="Novo produto (outros)")
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, price, per_m2 = dlg.get_values()
            r = self.others_table.rowCount()
            self.others_table.insertRow(r)
            self.others_table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
            self.others_table.setItem(r, 1, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            self.others_table.setItem(r, 2, QtWidgets.QTableWidgetItem("Sim" if per_m2 else "Não"))

    def _on_others_edit(self):
        r = self.others_table.currentRow()
        if r < 0:
            return
        name = self.others_table.item(r, 0).text()
        price = float(self.others_table.item(r, 1).text() or 0)
        per_m2 = (self.others_table.item(r, 2).text().strip().lower() == "sim")
        dlg = ProductPriceDialog(self, title="Editar produto (outros)", default_name=name, default_price=price, default_per_m2=per_m2)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, price, per_m2 = dlg.get_values()
            self.others_table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
            self.others_table.setItem(r, 1, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            self.others_table.setItem(r, 2, QtWidgets.QTableWidgetItem("Sim" if per_m2 else "Não"))

    def _on_others_remove(self):
        self._table_remove_current(self.others_table)

    def _table_add_row(self, table: QtWidgets.QTableWidget, headers: list[str]):
        row = table.rowCount()
        table.insertRow(row)
        for col in range(table.columnCount()):
            table.setItem(row, col, QtWidgets.QTableWidgetItem(""))
        table.setCurrentCell(row, 0)

    def _table_edit_current(self, table: QtWidgets.QTableWidget):
        row = table.currentRow()
        if row < 0:
            return
        table.editItem(table.item(row, 0))

    def _table_remove_current(self, table: QtWidgets.QTableWidget):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)


class PriceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Preço")
        self.setModal(True)
        self.resize(300, 200)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QFormLayout(self)
        
        self.tecido = QtWidgets.QComboBox()
        self.tecido.addItems(["Dryfit", "Helanca"])
        layout.addRow("Tecido:", self.tecido)
        
        self.manga = QtWidgets.QComboBox()
        self.manga.addItems(["Curta", "Longa"])
        layout.addRow("Manga:", self.manga)
        
        self.tamanho = QtWidgets.QLineEdit()
        self.tamanho.setPlaceholderText("Ex: PP, P, M, G, GG, XG, 2, 4, 6...")
        layout.addRow("Tamanho:", self.tamanho)
        
        self.preco = QtWidgets.QDoubleSpinBox()
        self.preco.setRange(0, 9999)
        self.preco.setDecimals(2)
        self.preco.setSuffix(" R$")
        layout.addRow("Preço:", self.preco)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | 
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return (
            self.tecido.currentText(),
            self.manga.currentText(),
            self.tamanho.text(),
            self.preco.value()
        )


class ProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, current_name=""):
        super().__init__(parent)
        self.setWindowTitle("Produto")
        self.setModal(True)
        self.resize(300, 150)
        self._init_ui(current_name)

    def _init_ui(self, current_name):
        layout = QtWidgets.QFormLayout(self)
        
        self.product_name = QtWidgets.QLineEdit()
        self.product_name.setText(current_name)
        self.product_name.setPlaceholderText("Nome do produto")
        layout.addRow("Nome:", self.product_name)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | 
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_product_name(self):
        return self.product_name.text()


class ProductPriceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, title: str = "Produto", default_name: str = "", default_price: float = 0.0, default_per_m2: bool = False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(360, 180)
        self._init_ui(default_name, default_price, default_per_m2)

    def _init_ui(self, default_name: str, default_price: float, default_per_m2: bool):
        form = QtWidgets.QFormLayout(self)
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setText(default_name)
        form.addRow("Nome:", self.name_edit)

        self.price_edit = QtWidgets.QDoubleSpinBox()
        self.price_edit.setRange(0, 999999)
        self.price_edit.setDecimals(2)
        self.price_edit.setSuffix(" R$")
        self.price_edit.setValue(default_price)
        form.addRow("Preço:", self.price_edit)

        self.per_m2_cb = QtWidgets.QCheckBox("Preço por m²")
        self.per_m2_cb.setChecked(default_per_m2)
        form.addRow("Cobrança:", self.per_m2_cb)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def get_values(self):
        return (
            self.name_edit.text().strip(),
            float(self.price_edit.value()),
            bool(self.per_m2_cb.isChecked()),
        )
