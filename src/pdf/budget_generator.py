from dataclasses import dataclass
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from datetime import date

from ..core.utils import cm
from ..core.simulator_models import Budget, ProductItem


class BudgetPDF:
    A4_WIDTH_CM = 21.0
    A4_HEIGHT_CM = 29.7

    def __init__(self, logos_dir: str = "public") -> None:
        self.path_manauara_logo = f"{logos_dir}/manauara_design.svg"

    def _draw_svg(self, c: canvas.Canvas, path: str, x: float, y: float, w_cm: float, h_cm: float) -> None:
        try:
            drawing = svg2rlg(path)
            if drawing:
                scale_x = cm(w_cm) / drawing.width
                scale_y = cm(h_cm) / drawing.height
                drawing.scale(scale_x, scale_y)
                renderPDF.draw(drawing, c, x, y)
        except Exception:
            c.rect(x, y, cm(w_cm), cm(h_cm))

    def _draw_text(self, c: canvas.Canvas, text: str, x: float, y: float, font: str = "Helvetica", size: float = 12) -> None:
        c.setFont(font, size)
        c.drawString(x, y, text)

    def _draw_text_centered(self, c: canvas.Canvas, text: str, x: float, y: float, font: str = "Helvetica", size: float = 12) -> None:
        c.setFont(font, size)
        text_width = c.stringWidth(text, font, size)
        c.drawString(x - text_width / 2, y, text)

    def _draw_header(self, c: canvas.Canvas, x: float, y: float) -> None:
        # Logo Manauara
        self._draw_svg(c, self.path_manauara_logo, x, y, 4.0, 2.0)
        
        # Título
        self._draw_text(c, "ORÇAMENTO", x + cm(8), y + cm(1.5), "Helvetica-Bold", 24)
        
        # Data
        self._draw_text(c, f"Data: {date.today().strftime('%d/%m/%Y')}", x + cm(8), y + cm(0.8), "Helvetica", 12)

    def _draw_client_info(self, c: canvas.Canvas, x: float, y: float, budget: Budget) -> None:
        self._draw_text(c, "DADOS DO CLIENTE", x, y, "Helvetica-Bold", 14)
        
        client_y = y - cm(0.8)
        self._draw_text(c, f"Nome: {budget.client.name}", x, client_y, "Helvetica", 12)
        
        client_y -= cm(0.5)
        self._draw_text(c, f"Telefone: {budget.client.phone}", x, client_y, "Helvetica", 12)
        
        if budget.client.email:
            client_y -= cm(0.5)
            self._draw_text(c, f"Email: {budget.client.email}", x, client_y, "Helvetica", 12)

    def _draw_products_table(self, c: canvas.Canvas, x: float, y: float, budget: Budget) -> None:
        self._draw_text(c, "PRODUTOS", x, y, "Helvetica-Bold", 14)
        
        # Cabeçalho da tabela
        table_y = y - cm(0.8)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, table_y, "Item")
        c.drawString(x + cm(2), table_y, "Descrição")
        c.drawString(x + cm(10), table_y, "Qtd")
        c.drawString(x + cm(12), table_y, "Preço Unit.")
        c.drawString(x + cm(15), table_y, "Total")
        
        # Linha separadora
        c.line(x, table_y - cm(0.2), x + cm(18), table_y - cm(0.2))
        
        # Produtos
        current_y = table_y - cm(0.6)
        c.setFont("Helvetica", 9)
        
        for i, item in enumerate(budget.items, 1):
            # Item
            c.drawString(x, current_y, str(i))
            
            # Descrição
            description = self._format_product_description(item)
            c.drawString(x + cm(2), current_y, description)
            
            # Quantidade
            c.drawString(x + cm(10), current_y, str(item.quantity))
            
            # Preço unitário
            unit_price = self._calculate_unit_price(item)
            c.drawString(x + cm(12), current_y, f"R$ {unit_price:.2f}")
            
            # Total do item
            item_total = unit_price * item.quantity
            c.drawString(x + cm(15), current_y, f"R$ {item_total:.2f}")
            
            current_y -= cm(0.4)
            
            # Criação de arte se houver
            if item.art_creation_price and item.art_creation_price > 0:
                current_y -= cm(0.2)
                c.drawString(x + cm(2), current_y, f"  + Criação de arte: R$ {item.art_creation_price:.2f}")
                current_y -= cm(0.3)

    def _format_product_description(self, item: ProductItem) -> str:
        """Formata descrição do produto"""
        if item.product_type == "camiseta":
            return f"Camiseta {item.fabric.title()} {item.sleeve.title()} {item.size}"
        elif item.product_type == "conjunto":
            return f"Conjunto {item.fabric.replace('_', ' ').title()} {item.sleeve.title()}"
        elif item.product_type == "short":
            return "Short"
        elif item.product_type == "comunicacao_visual":
            area = (item.width_cm or 0) * (item.height_cm or 0) / 10000
            return f"{item.visual_type.title()} {item.width_cm}x{item.height_cm}cm ({area:.2f}m²)"
        elif item.product_type == "criacao_arte":
            return f"Criação de Arte - R$ {item.art_creation_price:.2f}"
        return "Produto"

    def _calculate_unit_price(self, item: ProductItem) -> Decimal:
        """Calcula preço unitário do item"""
        # Esta é uma versão simplificada - em produção, usaria a PriceDatabase
        if item.product_type == "camiseta":
            if item.fabric == "dryfit":
                if item.sleeve == "curta":
                    return Decimal('40.00') if item.size in ['PP', 'P', 'M', 'G'] else Decimal('45.00')
                else:  # longa
                    if item.size in ['PP', 'P', 'M', 'G']:
                        return Decimal('45.00')
                    elif item.size == 'GG':
                        return Decimal('50.00')
                    else:
                        return Decimal('53.00')
            else:  # helanca
                if item.sleeve == "curta":
                    return Decimal('35.00') if item.size in ['PP', 'P', 'M', 'G'] else Decimal('40.00')
                else:  # longa
                    if item.size in ['PP', 'P', 'M', 'G']:
                        return Decimal('40.00')
                    elif item.size == 'GG':
                        return Decimal('45.00')
                    else:
                        return Decimal('48.00')
        elif item.product_type == "short":
            return Decimal('25.00')
        elif item.product_type == "comunicacao_visual":
            area = (item.width_cm or 0) * (item.height_cm or 0) / 10000
            price_per_m2 = Decimal('60.00') if item.visual_type == 'lona' else Decimal('50.00')
            return price_per_m2 * Decimal(str(area))
        elif item.product_type == "criacao_arte":
            return item.art_creation_price or Decimal('0')
        
        return Decimal('0')

    def _draw_totals(self, c: canvas.Canvas, x: float, y: float, budget: Budget) -> None:
        # Linha separadora
        c.line(x, y, x + cm(18), y)
        y -= cm(0.3)
        
        # Subtotal
        c.setFont("Helvetica", 10)
        c.drawString(x + cm(12), y, f"Subtotal: R$ {budget.subtotal:.2f}")
        y -= cm(0.4)
        
        # Criação de arte
        if budget.art_creation_total > 0:
            c.drawString(x + cm(12), y, f"Criação de Arte: R$ {budget.art_creation_total:.2f}")
            y -= cm(0.4)
        
        # Desconto
        if budget.discount:
            discount_text = f"Desconto ({budget.discount.description}): R$ {budget.discount.value:.2f}"
            c.drawString(x + cm(12), y, discount_text)
            y -= cm(0.4)
        
        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + cm(12), y, f"TOTAL: R$ {budget.total:.2f}")

    def _draw_footer(self, c: canvas.Canvas, x: float, y: float) -> None:
        footer_text = "manauaradesig@gmail.com - Desenvolvido por Manauara Design - Todos os direitos reservados @2026"
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + cm(10), y, footer_text)

    def generate(self, budget: Budget, output_path: str) -> None:
        """Gera PDF do orçamento"""
        c = canvas.Canvas(output_path, pagesize=(cm(self.A4_WIDTH_CM), cm(self.A4_HEIGHT_CM)))
        c.setAuthor("Manauara Design")
        
        # Margens
        left_x = cm(1.5)
        top_y = cm(self.A4_HEIGHT_CM - 2)
        
        # Cabeçalho
        self._draw_header(c, left_x, top_y)
        
        # Informações do cliente
        client_y = top_y - cm(3)
        self._draw_client_info(c, left_x, client_y, budget)
        
        # Tabela de produtos
        products_y = client_y - cm(3)
        self._draw_products_table(c, left_x, products_y, budget)
        
        # Totais
        totals_y = products_y - cm(4)
        self._draw_totals(c, left_x, totals_y, budget)
        
        # Rodapé
        footer_y = cm(2)
        self._draw_footer(c, left_x, footer_y)
        
        c.showPage()
        c.save()
