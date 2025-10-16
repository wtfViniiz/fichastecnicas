# Fichas Técnicas - Manauara Design

Aplicativo desktop (Windows) em PyQt6 para gerar fichas técnicas em PDF no formato solicitado. Gera uma página A4 com duas fichas A5.

## Como rodar

1. Crie venv e instale dependências:
```
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```
2. Coloque os SVGs em `public/` com os nomes:
   - `ficha_tecnica.svg`
   - `manauara_design.svg`
3. Execute:
```
python -m src.main
```

## Estrutura
- `src/core` modelos e utilitários
- `src/pdf` gerador de PDF (ReportLab)
- `src/ui` interface PyQt6
- `public` assets SVG

## Notas de layout
- Todas as medidas em centímetros convertidas para pontos (72 dpi): 1 cm = 28.3464567 pt
- Datas: entrega = encomenda + 7 dias úteis (inclui sábado)
