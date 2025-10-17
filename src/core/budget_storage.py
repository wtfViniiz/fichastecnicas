import json
import os
from datetime import date, datetime
from typing import List, Dict, Optional
from decimal import Decimal

from .simulator_models import Budget, ClientInfo, ProductItem, Discount


class BudgetStorage:
    """Sistema de armazenamento e busca de orçamentos"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.budgets_file = os.path.join(storage_dir, "budgets.json")
        self._ensure_storage_dir()
        self._load_budgets()
    
    def _ensure_storage_dir(self):
        """Cria diretório de armazenamento se não existir"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def _load_budgets(self):
        """Carrega orçamentos do arquivo"""
        self.budgets: List[Dict] = []
        if os.path.exists(self.budgets_file):
            try:
                with open(self.budgets_file, 'r', encoding='utf-8') as f:
                    self.budgets = json.load(f)
            except Exception:
                self.budgets = []
    
    def _save_budgets(self):
        """Salva orçamentos no arquivo"""
        try:
            with open(self.budgets_file, 'w', encoding='utf-8') as f:
                json.dump(self.budgets, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar orçamentos: {e}")
    
    def save_budget(self, budget: Budget) -> str:
        """Salva um orçamento e retorna ID único"""
        budget_id = f"ORC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.budgets)}"
        
        budget_dict = {
            "id": budget_id,
            "client": {
                "name": budget.client.name,
                "phone": budget.client.phone,
                "email": budget.client.email
            },
            "items": [],
            "discount": None,
            "art_creation_total": float(budget.art_creation_total),
            "subtotal": float(budget.subtotal),
            "total": float(budget.total),
            "created_date": budget.created_date,
            "saved_date": datetime.now().isoformat()
        }
        
        # Converter itens
        for item in budget.items:
            item_dict = {
                "product_type": item.product_type,
                "fabric": item.fabric,
                "sleeve": item.sleeve,
                "size": item.size,
                "visual_type": item.visual_type,
                "quantity": item.quantity,
                "width_cm": item.width_cm,
                "height_cm": item.height_cm,
                "art_creation_price": float(item.art_creation_price) if item.art_creation_price else None
            }
            budget_dict["items"].append(item_dict)
        
        # Converter desconto
        if budget.discount:
            budget_dict["discount"] = {
                "type": budget.discount.type,
                "value": float(budget.discount.value),
                "description": budget.discount.description
            }
        
        self.budgets.append(budget_dict)
        self._save_budgets()
        return budget_id
    
    def load_budget(self, budget_id: str) -> Optional[Budget]:
        """Carrega um orçamento pelo ID"""
        for budget_dict in self.budgets:
            if budget_dict["id"] == budget_id:
                return self._dict_to_budget(budget_dict)
        return None
    
    def search_budgets(self, client_name: str = "", date_from: str = "", date_to: str = "") -> List[Dict]:
        """Busca orçamentos por critérios"""
        results = []
        
        for budget_dict in self.budgets:
            # Filtro por nome do cliente
            if client_name and client_name.lower() not in budget_dict["client"]["name"].lower():
                continue
            
            # Filtro por data
            if date_from or date_to:
                budget_date = budget_dict["created_date"]
                if date_from and budget_date < date_from:
                    continue
                if date_to and budget_date > date_to:
                    continue
            
            results.append(budget_dict)
        
        # Ordenar por data mais recente
        results.sort(key=lambda x: x["saved_date"], reverse=True)
        return results
    
    def get_recent_budgets(self, limit: int = 10) -> List[Dict]:
        """Retorna orçamentos mais recentes"""
        return sorted(self.budgets, key=lambda x: x["saved_date"], reverse=True)[:limit]
    
    def delete_budget(self, budget_id: str) -> bool:
        """Remove um orçamento"""
        for i, budget_dict in enumerate(self.budgets):
            if budget_dict["id"] == budget_id:
                del self.budgets[i]
                self._save_budgets()
                return True
        return False
    
    def _dict_to_budget(self, budget_dict: Dict) -> Budget:
        """Converte dicionário para objeto Budget"""
        client = ClientInfo(
            name=budget_dict["client"]["name"],
            phone=budget_dict["client"]["phone"],
            email=budget_dict["client"]["email"]
        )
        
        budget = Budget(
            client=client,
            created_date=budget_dict["created_date"]
        )
        
        # Converter itens
        for item_dict in budget_dict["items"]:
            item = ProductItem(
                product_type=item_dict["product_type"],
                fabric=item_dict.get("fabric"),
                sleeve=item_dict.get("sleeve"),
                size=item_dict.get("size"),
                visual_type=item_dict.get("visual_type"),
                quantity=item_dict["quantity"],
                width_cm=item_dict.get("width_cm"),
                height_cm=item_dict.get("height_cm"),
                art_creation_price=Decimal(str(item_dict["art_creation_price"])) if item_dict.get("art_creation_price") else None
            )
            budget.items.append(item)
        
        # Converter desconto
        if budget_dict.get("discount"):
            discount_dict = budget_dict["discount"]
            budget.discount = Discount(
                type=discount_dict["type"],
                value=Decimal(str(discount_dict["value"])),
                description=discount_dict["description"]
            )
        
        budget.art_creation_total = Decimal(str(budget_dict["art_creation_total"]))
        budget.subtotal = Decimal(str(budget_dict["subtotal"]))
        budget.total = Decimal(str(budget_dict["total"]))
        
        return budget
