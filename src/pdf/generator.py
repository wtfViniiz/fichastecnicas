from dataclasses import dataclass
from typing import Optional
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from datetime import date

from . import __init__  # noqa: F401
from ..core.models import OrderInfo, SizeTable
from ..core.utils import cm


@dataclass
class PDFOptions:
    output_path: str


class TechSheetPDF:
    A4_WIDTH_CM = 29.7
    A4_HEIGHT_CM = 21.0
    A5_WIDTH_CM = 14.85
    A5_HEIGHT_CM = 21.0

    FRONT_BOX_CM = (6.537, 5.798)
    IMAGE_MAX_CM = (4.494, 3.807)
    LOGO_FICHA_CM = (5.828, 1.896)
    LOGO_MANAUARA_CM = (4.149, 2.178)

    def __init__(self, logos_dir: str = "public") -> None:
        self.path_ficha_logo = f"{logos_dir}/ficha_tecnica.svg"
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

    def _draw_image_fit(self, c: canvas.Canvas, img_path: Optional[str], x: float, y: float, w_cm: float, h_cm: float) -> None:
        if not img_path:
            return
        try:
            img = ImageReader(img_path)
            iw, ih = img.getSize()
            max_w, max_h = cm(w_cm), cm(h_cm)
            ratio = min(max_w / iw, max_h / ih)
            w, h = iw * ratio, ih * ratio
            c.drawImage(img, x + (max_w - w) / 2, y + (max_h - h) / 2, width=w, height=h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    def _draw_grid(self, c: canvas.Canvas, x: float, y: float, w: float, h: float, rows: int, cols: int) -> None:
        c.rect(x, y, w, h)
        row_h = h / rows
        col_w = w / cols
        for i in range(1, rows):
            c.line(x, y + i * row_h, x + w, y + i * row_h)
        for j in range(1, cols):
            c.line(x + j * col_w, y, x + j * col_w, y + h)

    def _draw_text(self, c: canvas.Canvas, text: str, x: float, y: float, font: str = "Helvetica", size: float = 12) -> None:
        c.setFont(font, size)
        c.drawString(x, y, text)

    def _wrap_text(self, c: canvas.Canvas, text: str, x: float, y: float, width_cm: float, line_height: float, font: str, size: float) -> None:
        c.setFont(font, size)
        max_w = cm(width_cm)
        words = text.split()
        line = ""
        cur_y = y
        for w in words:
            candidate = (line + " " + w).strip()
            if c.stringWidth(candidate, font, size) <= max_w:
                line = candidate
            else:
                c.drawString(x, cur_y, line)
                cur_y -= line_height
                line = w
        if line:
            c.drawString(x, cur_y, line)

    def _draw_header(self, c: canvas.Canvas, x: float, y: float) -> None:
        self._draw_svg(c, self.path_ficha_logo, x, y, self.LOGO_FICHA_CM[0], self.LOGO_FICHA_CM[1])
        manauara_x = x + cm(8.5)
        self._draw_svg(c, self.path_manauara_logo, manauara_x, y, self.LOGO_MANAUARA_CM[0], self.LOGO_MANAUARA_CM[1])

    def _draw_text_centered(self, c: canvas.Canvas, text: str, x: float, y: float, font: str = "Helvetica", size: float = 12) -> None:
        c.setFont(font, size)
        text_width = c.stringWidth(text, font, size)
        c.drawString(x - text_width / 2, y, text)

    def _draw_table(self, c: canvas.Canvas, x: float, y: float, table: SizeTable) -> None:
        total_w_cm = 12.7
        total_h_cm = 4.3
        block_w_cm = total_w_cm / 3
        block_h_cm = total_h_cm
        cols = 3
        rows = 8  # 1 título + 1 cabeçalho + 6 tamanhos

        y -= cm(0.5)  

        for idx, gender in enumerate(["feminino", "masculino", "infantil"]):
            bx = x + cm(idx * block_w_cm)
            by = y

            # dimensões em pontos
            bw = cm(block_w_cm)
            bh = cm(block_h_cm)

            # Linhas horizontais internas (começam da 2ª linha pra baixo)
            row_h = bh / rows
            for r in range(1, rows):
                c.line(bx, by - r * row_h, bx + bw, by - r * row_h)

            # Linhas verticais (somente da 2ª linha pra baixo)
            col_w = bw / cols
            for j in range(1, cols):
                c.line(bx + j * col_w, by - row_h, bx + j * col_w, by - bh)

            # Linha grossa de separação entre blocos
            if idx < 2:  # evita desenhar após o último bloco
                c.setLineWidth(2)
                c.line(bx + bw, by, bx + bw, by - bh)
                c.setLineWidth(1)

            # --- TEXTOS ---

            # Título principal (1ª linha, centralizado)
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(bx + bw / 2, by - row_h / 1.5, gender.upper())

            # Cabeçalho "CURTA" e "LONGA" (2ª linha)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(bx + col_w * 1.5, by - row_h * 1.6, "CURTA")
            c.drawCentredString(bx + col_w * 2.5, by - row_h * 1.6, "LONGA")

            # Tamanhos a partir da 3ª linha
            c.setFont("Helvetica-Bold", 9)
            sizes = ["PP", "P", "M", "G", "GG", "XG"]
            for r, size in enumerate(sizes, start=2):
                # desce 0.121 cm os tamanhos
                text_y = by - row_h * (r + 0.4) - cm(0.121)
                c.drawCentredString(bx + col_w * 0.5, text_y, size)

                # valores das colunas CURTA e LONGA
                for j, sleeve in enumerate(["curta", "longa"]):
                    val = table.get_quantity(gender, size, sleeve)
                    if val:
                        col_x = bx + col_w * (1.5 + j)
                        c.drawCentredString(col_x, text_y, f"{val:02d}")



    def _draw_form(self, c: canvas.Canvas, x: float, y: float, info: OrderInfo, table: SizeTable) -> None:
        self._draw_text(c, "FICHA", x + cm(0.8), y - cm(0.6), "Helvetica-Bold", 18)
        self._draw_text(c, "TÉCNICA", x + cm(0.8), y - cm(1.2), "Helvetica-Bold", 18)
        self._draw_svg(c, self.path_manauara_logo, x + cm(8.5), y - cm(0.07) - cm(self.LOGO_MANAUARA_CM[1]), 
        self.LOGO_MANAUARA_CM[0], self.LOGO_MANAUARA_CM[1])

        client_y = y - cm(2.8)
        self._draw_text(c, "CLIENTE", x + cm(0.8), client_y + cm(0.22), "Helvetica-Bold", 12)
        c.rect(x + cm(0.8), client_y - cm(1), cm(6.5), cm(0.88))
        client_name = (info.client_name or "Nome")[:20]  # pega no máximo 20 caracteres
        self._draw_text(c, client_name, x + cm(1.0), client_y - cm(0.8), "Helvetica", 15)


        qtd_y = client_y
        grid_x = x + cm(7.5)
        grid_w = cm(6.5)
        grid_h = cm(1.3)
        self._draw_grid(c, grid_x, qtd_y - cm(1.0), grid_w, grid_h, 2, 3)

        col_w = grid_w / 3
        centers_x = [grid_x + col_w/2, grid_x + col_w*1.5, grid_x + col_w*2.5]
        text_y = qtd_y - cm(0.15)
        c.setFont("Helvetica-Bold", 8.6)
        c.drawCentredString(centers_x[0], text_y, "QTD")
        c.drawCentredString(centers_x[1], text_y, "ENCOMENDA")
        c.drawCentredString(centers_x[2], text_y, "ENTREGA")
        
        row_h = grid_h / 2
        values_y = (qtd_y - cm(1.1)) + row_h / 2
        total_qty = table.total()
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(centers_x[0], values_y, f"{total_qty:02d}")

        c.setFont("Helvetica", 10)
        c.drawCentredString(centers_x[1], values_y, info.order_date.strftime('%d/%m/%y'))
        c.drawCentredString(centers_x[2], values_y, info.delivery_date.strftime('%d/%m/%y')) 

        # Dimensões do box
        box_y = y - cm(4.5) - cm(self.FRONT_BOX_CM[1])
        box_w, box_h = cm(self.FRONT_BOX_CM[0]), cm(self.FRONT_BOX_CM[1])

        # Coordenadas centrais dos quadrados
        center_x_front = x + cm(0.8) + box_w / 2
        center_x_back = x + cm(7.4) + box_w / 2
        text_y = box_y + box_h + cm(0.2)  # altura do texto

        # Desenha retângulos
        c.rect(x + cm(0.8), box_y, box_w, box_h)
        c.rect(x + cm(7.4), box_y, box_w, box_h)

        # Desenha textos centralizados horizontalmente usando a função já existente
        self._draw_text_centered(c, "FRENTE", center_x_front, text_y, "Helvetica-Bold", 12)
        self._draw_text_centered(c, "COSTA", center_x_back, text_y, "Helvetica-Bold", 12)

        img_front_x = center_x_front - cm(self.IMAGE_MAX_CM[0]) / 2
        img_back_x = center_x_back - cm(self.IMAGE_MAX_CM[0]) / 2
        img_y = box_y + (box_h - cm(self.IMAGE_MAX_CM[1])) / 2

        self._draw_image_fit(c, info.front_image_path, img_front_x, img_y, self.IMAGE_MAX_CM[0], self.IMAGE_MAX_CM[1])
        self._draw_image_fit(c, info.back_image_path, img_back_x, img_y, self.IMAGE_MAX_CM[0], self.IMAGE_MAX_CM[1])

        fields_y = y - cm(11.0)
        fields = [
            ("TIPO DE TECIDO", info.fabric.replace('_', ' ').upper()),
            ("TIPO DE GOLA", info.neck.replace('_', ' ').upper()),
            ("CONJUNTO", "SIM" if info.is_set else "NÃO"),
        ]

        for idx, (title, value) in enumerate(fields):
            field_y = fields_y - cm(idx * 1.35)
            
            # Texto do título ajustado
            title_x = x + cm(0.8) + cm(0.043)
            title_y = field_y + cm(0.087)
            self._draw_text(c, title, title_x, title_y, "Helvetica-Bold", 10)
            
            # Caixa ajustada
            box_w, box_h = cm(5.805), cm(0.669)
            c.rect(x + cm(0.8), field_y - box_h, box_w, box_h)
            
            # Texto da resposta centralizado verticalmente
            text_y_val = (field_y - box_h) + (box_h / 2) - (11 / 2) * 0.3  # fonte tamanho 11
            self._draw_text(c, value, x + cm(1.0), text_y_val, "Helvetica", 11)

        desc_y = fields_y
        self._draw_text(c,"DESCRIÇÃO",x + cm(7.5 - 0.188),desc_y + cm(0.103),"Helvetica-Bold",10 )
        c.roundRect(x + cm(7.5 - 0.2), desc_y - cm(3.229), cm(6.5), cm(3.229), 4)
        if info.description:
            truncated_desc = info.description[:260]  # pega no máximo 270 caracteres
            self._wrap_text(
                c,
                truncated_desc,
                x + cm(7.5 - 0.2 + 0.2),
                desc_y - cm(0.5),
                6.153,
                12,
                "Helvetica",
                10
            )


        table_y = y - cm(14.5)
        self._draw_table(c, x + cm(0.8), table_y, table)

        footer_width_cm = 11.0
        footer_center_x = x + cm(1.2) + cm(footer_width_cm)/2
        footer_y = cm(0.5)
        footer_text = "   manauaradesig@gmail.com Desenvolvido por Manauara Design - Todos os direitos reservados @2026"
        c.setFont("Helvetica", 8)
        c.drawCentredString(footer_center_x, footer_y, footer_text)

    def build(self, info: OrderInfo, table: SizeTable, options: PDFOptions) -> None:
        c = canvas.Canvas(options.output_path, pagesize=(cm(self.A4_WIDTH_CM), cm(self.A4_HEIGHT_CM)))
        c.setAuthor("Manauara Design")

        left_x = cm(0.5)
        top_margin = cm(self.A4_HEIGHT_CM - 0.5)
        self._draw_form(c, left_x, top_margin, info, table)

        right_x = left_x + cm(self.A5_WIDTH_CM) + cm(-0.1)
        self._draw_form(c, right_x, top_margin, info, table)

        c.showPage()
        c.save()
