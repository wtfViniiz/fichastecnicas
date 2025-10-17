from typing import List, Tuple
from decimal import Decimal

from .simulator_models import ProductItem, Budget


class BudgetValidator:
    """Validador de orçamentos com verificações de consistência"""
    
    MIN_QUANTITY_CAMISETA = 5
    MIN_QUANTITY_CONJUNTO = 1
    MIN_QUANTITY_SHORT = 1
    MIN_QUANTITY_VISUAL = 1
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_budget(self, budget: Budget) -> Tuple[bool, List[str], List[str]]:
        """Valida orçamento completo e retorna (válido, erros, avisos)"""
        self.errors.clear()
        self.warnings.clear()
        
        # Validar cliente
        self._validate_client(budget)
        
        # Validar produtos
        self._validate_products(budget)
        
        # Validar totais
        self._validate_totals(budget)
        
        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()
    
    def _validate_client(self, budget: Budget):
        """Valida dados do cliente"""
        if not budget.client.name.strip():
            self.errors.append("Nome do cliente é obrigatório.")
        
        if not budget.client.phone.strip():
            self.errors.append("Telefone do cliente é obrigatório.")
        elif len(budget.client.phone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")) < 10:
            self.warnings.append("Telefone do cliente pode estar incompleto.")
    
    def _validate_products(self, budget: Budget):
        """Valida produtos do orçamento"""
        if not budget.items:
            self.errors.append("Orçamento deve ter pelo menos um produto.")
            return
        
        # Regra especial: camisetas podem somar tamanhos/variações até atingir mínimo
        total_camisas = 0
        for item in budget.items:
            if item.product_type == "camiseta":
                try:
                    total_camisas += int(item.quantity)
                except Exception:
                    pass

        for i, item in enumerate(budget.items, 1):
            self._validate_product(item, i)

        # Se houver ao menos uma camiseta, valida mínimo somado
        if total_camisas > 0 and total_camisas < self.MIN_QUANTITY_CAMISETA:
            self.errors.append(
                f"Quantidade mínima para camisetas (somadas) é {self.MIN_QUANTITY_CAMISETA} unidades. Atual: {total_camisas}."
            )
    
    def _validate_product(self, item: ProductItem, position: int):
        """Valida um produto específico"""
        prefix = f"Produto {position}:"
        
        # Validar quantidade mínima por item (exceto camisetas, que usam soma global)
        if item.product_type == "camiseta":
            pass
        elif item.product_type == "conjunto":
            if item.quantity < self.MIN_QUANTITY_CONJUNTO:
                self.errors.append(f"{prefix} Quantidade mínima para conjuntos é {self.MIN_QUANTITY_CONJUNTO} unidade.")
        elif item.product_type == "short":
            if item.quantity < self.MIN_QUANTITY_SHORT:
                self.errors.append(f"{prefix} Quantidade mínima para shorts é {self.MIN_QUANTITY_SHORT} unidade.")
        elif item.product_type == "comunicacao_visual":
            if item.quantity < self.MIN_QUANTITY_VISUAL:
                self.errors.append(f"{prefix} Quantidade mínima para comunicação visual é {self.MIN_QUANTITY_VISUAL} unidade.")
            
            # Validar dimensões
            if not item.width_cm or item.width_cm <= 0:
                self.errors.append(f"{prefix} Largura deve ser maior que zero.")
            if not item.height_cm or item.height_cm <= 0:
                self.errors.append(f"{prefix} Altura deve ser maior que zero.")
        
        # Validar campos obrigatórios por tipo
        if item.product_type == "camiseta":
            if not item.fabric:
                self.errors.append(f"{prefix} Tecido é obrigatório para camisetas.")
            if not item.sleeve:
                self.errors.append(f"{prefix} Tipo de manga é obrigatório para camisetas.")
            if not item.size:
                self.errors.append(f"{prefix} Tamanho é obrigatório para camisetas.")
        
        elif item.product_type == "conjunto":
            if not item.fabric:
                self.errors.append(f"{prefix} Tipo de conjunto é obrigatório.")
            if not item.sleeve:
                self.errors.append(f"{prefix} Tipo de manga é obrigatório para conjuntos.")
        
        elif item.product_type == "comunicacao_visual":
            if not item.visual_type:
                self.errors.append(f"{prefix} Tipo de comunicação visual é obrigatório.")
        
        elif item.product_type == "criacao_arte":
            if not item.art_creation_price or item.art_creation_price <= 0:
                self.errors.append(f"{prefix} Valor da criação de arte deve ser maior que zero.")
    
    def _validate_totals(self, budget: Budget):
        """Valida totais do orçamento"""
        if budget.subtotal < 0:
            self.errors.append("Subtotal não pode ser negativo.")
        
        if budget.total < 0:
            self.errors.append("Total não pode ser negativo.")
        
        if budget.total == 0:
            self.warnings.append("Total do orçamento é zero. Verifique os produtos adicionados.")
        
        # Verificar se desconto não é maior que subtotal
        if budget.discount:
            if budget.discount.type == "percentage" and budget.discount.value > 100:
                self.errors.append("Desconto percentual não pode ser maior que 100%.")
            elif budget.discount.type == "fixed" and budget.discount.value > budget.subtotal:
                self.warnings.append("Desconto em valor fixo é maior que o subtotal.")
    
    def get_validation_summary(self, budget: Budget) -> str:
        """Retorna resumo das validações"""
        is_valid, errors, warnings = self.validate_budget(budget)
        
        summary = []
        if errors:
            summary.append("❌ ERROS:")
            for error in errors:
                summary.append(f"  • {error}")
        
        if warnings:
            summary.append("\n⚠️ AVISOS:")
            for warning in warnings:
                summary.append(f"  • {warning}")
        
        if not errors and not warnings:
            summary.append("✅ Orçamento válido!")
        
        return "\n".join(summary)
