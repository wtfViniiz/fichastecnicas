from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DiscountSuggestion:
    label: str  # "baixa sugerida"
    percent: Optional[int] = None  # desconto percentual sugerido
    reason: str = ""


class DiscountSuggester:
    """Heurística simples para sugerir descontos.

    Fatores:
    - Histórico do cliente (gasto total e frequência)
    - Ticket atual
    - Quantidade total de itens
    """

    @staticmethod
    def suggest(total_current: float, items_count: int, client_total_spent: float, client_budgets_count: int) -> Optional[DiscountSuggestion]:
        # Se não há histórico, só sugere em casos realmente excepcionais
        if client_budgets_count == 0 and client_total_spent <= 0:
            exceptional = 0
            if total_current >= 3000:
                exceptional += 3
            elif total_current >= 2000:
                exceptional += 2
            if items_count >= 100:
                exceptional += 2
            elif items_count >= 50:
                exceptional += 1
            exceptional = max(0, min(exceptional, 10))
            if exceptional <= 0:
                return None
            return DiscountSuggestion(label="baixa sugerida", percent=exceptional, reason="Ticket/volume excepcionais")

        # Clientes com histórico: base pela fidelidade
        base = 0
        if client_budgets_count >= 15 or client_total_spent >= 10000:
            base = 12
        elif client_budgets_count >= 8 or client_total_spent >= 5000:
            base = 9
        elif client_budgets_count >= 4 or client_total_spent >= 2000:
            base = 6
        elif client_budgets_count >= 2 or client_total_spent >= 800:
            base = 4

        # Ajuste por ticket atual
        if total_current >= 2500:
            base += 3
        elif total_current >= 1500:
            base += 2
        elif total_current >= 800:
            base += 1

        # Ajuste por volume de itens
        if items_count >= 80:
            base += 2
        elif items_count >= 30:
            base += 1

        # Limites e piso mínimo para não sugerir descontos muito pequenos
        base = max(0, min(base, 20))
        if base < 3:
            return None

        return DiscountSuggestion(label="baixa sugerida", percent=base, reason="Histórico e ticket/volume atuais")


