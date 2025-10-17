from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from decimal import Decimal

# Tipos de produtos
ProductType = Literal["camiseta", "conjunto", "short", "comunicacao_visual", "criacao_arte"]
FabricType = Literal["dryfit", "helanca"]
SleeveType = Literal["curta", "longa"]
SizeType = Literal["PP", "P", "M", "G", "GG", "XG", "XGG", "XG3", "2", "4", "6", "8", "10", "12", "14", "16"]
VisualType = Literal["lona", "adesivo", "adesivo_perfurado", "banner"]

# Tipos de cliente
ClientType = Literal["normal", "terceiro"]

@dataclass
class ProductPrice:
    """Preço base de um produto"""
    fabric: FabricType
    sleeve: SleeveType
    size: SizeType
    price: Decimal
    client_type: ClientType = "normal"

@dataclass
class VisualProductPrice:
    """Preço por m² para produtos de comunicação visual"""
    product_type: VisualType
    price_per_m2: Decimal

@dataclass
class ProductItem:
    """Item individual no orçamento"""
    product_type: ProductType
    fabric: Optional[FabricType] = None
    sleeve: Optional[SleeveType] = None
    size: Optional[SizeType] = None
    visual_type: Optional[VisualType] = None
    other_name: Optional[str] = None  # Produtos cadastrados no Admin
    quantity: int = 1
    width_cm: Optional[float] = None  # Para comunicação visual
    height_cm: Optional[float] = None  # Para comunicação visual
    art_creation_price: Optional[Decimal] = None  # Criação de arte opcional

@dataclass
class ClientInfo:
    """Informações do cliente"""
    name: str
    phone: str
    email: Optional[str] = None

@dataclass
class Discount:
    """Desconto aplicado"""
    type: Literal["percentage", "fixed"]
    value: Decimal
    description: str = ""

@dataclass
class Budget:
    """Orçamento completo"""
    client: ClientInfo
    items: List[ProductItem] = field(default_factory=list)
    discount: Optional[Discount] = None
    art_creation_total: Decimal = Decimal('0')
    subtotal: Decimal = Decimal('0')
    total: Decimal = Decimal('0')
    created_date: str = ""

class PriceDatabase:
    """Base de dados de preços"""
    
    def __init__(self):
        self.camiseta_prices = self._load_camiseta_prices()
        self.conjunto_prices = self._load_conjunto_prices()
        self.visual_prices = self._load_visual_prices()
        self.other_products = self._load_other_products()
    
    def _load_camiseta_prices(self) -> Dict[tuple, Decimal]:
        """Carrega preços das camisetas baseado na tabela fornecida"""
        prices = {}
        
        # DRYFIT - MANGA CURTA
        prices[("dryfit", "curta", "PP", "normal")] = Decimal('40.00')
        prices[("dryfit", "curta", "P", "normal")] = Decimal('40.00')
        prices[("dryfit", "curta", "M", "normal")] = Decimal('40.00')
        prices[("dryfit", "curta", "G", "normal")] = Decimal('40.00')
        prices[("dryfit", "curta", "GG", "normal")] = Decimal('45.00')
        prices[("dryfit", "curta", "XG", "normal")] = Decimal('45.00')
        prices[("dryfit", "curta", "XGG", "normal")] = Decimal('45.00')
        prices[("dryfit", "curta", "XG3", "normal")] = Decimal('45.00')
        
        # DRYFIT - MANGA LONGA
        prices[("dryfit", "longa", "PP", "normal")] = Decimal('45.00')
        prices[("dryfit", "longa", "P", "normal")] = Decimal('45.00')
        prices[("dryfit", "longa", "M", "normal")] = Decimal('45.00')
        prices[("dryfit", "longa", "G", "normal")] = Decimal('45.00')
        prices[("dryfit", "longa", "GG", "normal")] = Decimal('50.00')
        prices[("dryfit", "longa", "XG", "normal")] = Decimal('53.00')
        prices[("dryfit", "longa", "XGG", "normal")] = Decimal('53.00')
        prices[("dryfit", "longa", "XG3", "normal")] = Decimal('53.00')
        
        # HELANCA - MANGA CURTA
        prices[("helanca", "curta", "PP", "normal")] = Decimal('35.00')
        prices[("helanca", "curta", "P", "normal")] = Decimal('35.00')
        prices[("helanca", "curta", "M", "normal")] = Decimal('35.00')
        prices[("helanca", "curta", "G", "normal")] = Decimal('35.00')
        prices[("helanca", "curta", "GG", "normal")] = Decimal('40.00')
        prices[("helanca", "curta", "XG", "normal")] = Decimal('40.00')
        prices[("helanca", "curta", "XGG", "normal")] = Decimal('40.00')
        prices[("helanca", "curta", "XG3", "normal")] = Decimal('40.00')
        
        # HELANCA - MANGA LONGA
        prices[("helanca", "longa", "PP", "normal")] = Decimal('40.00')
        prices[("helanca", "longa", "P", "normal")] = Decimal('40.00')
        prices[("helanca", "longa", "M", "normal")] = Decimal('40.00')
        prices[("helanca", "longa", "G", "normal")] = Decimal('40.00')
        prices[("helanca", "longa", "GG", "normal")] = Decimal('45.00')
        prices[("helanca", "longa", "XG", "normal")] = Decimal('48.00')
        prices[("helanca", "longa", "XGG", "normal")] = Decimal('48.00')
        prices[("helanca", "longa", "XG3", "normal")] = Decimal('48.00')
        
        return prices
    
    def _load_conjunto_prices(self) -> Dict[tuple, Decimal]:
        """Carrega preços dos conjuntos baseado na tabela anexada"""
        prices = {}
        
        # Conjuntos Helanca + Tactel
        prices[("helanca_tactel", "curta", "normal")] = Decimal('58.00')
        prices[("helanca_tactel", "longa", "normal")] = Decimal('63.00')
        prices[("helanca_tactel", "curta", "terceiro")] = Decimal('49.00')
        prices[("helanca_tactel", "longa", "terceiro")] = Decimal('54.00')
        
        # Conjuntos Todo Helanca
        prices[("todo_helanca", "curta", "normal")] = Decimal('68.00')
        prices[("todo_helanca", "longa", "normal")] = Decimal('70.00')
        prices[("todo_helanca", "curta", "terceiro")] = Decimal('59.00')
        prices[("todo_helanca", "longa", "terceiro")] = Decimal('62.00')
        
        # Conjuntos Dryfit + Helanca
        prices[("dryfit_helanca", "curta", "normal")] = Decimal('73.00')
        prices[("dryfit_helanca", "longa", "normal")] = Decimal('75.00')
        prices[("dryfit_helanca", "curta", "terceiro")] = Decimal('64.00')
        prices[("dryfit_helanca", "longa", "terceiro")] = Decimal('67.00')
        
        return prices
    
    def _load_visual_prices(self) -> Dict[str, Decimal]:
        """Carrega preços da comunicação visual, mesclando com config/prices.json se existir."""
        base = {
            "lona": Decimal('60.00'),
            "adesivo": Decimal('50.00'),
            "adesivo_perfurado": Decimal('70.00'),
            "banner": Decimal('50.00')
        }
        import os, json
        cfg = os.path.join("config", "prices.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for v in data.get("visual", []):
                        name = str(v.get("nome", "")).strip()
                        price = Decimal(str(v.get("preco_m2", 0)))
                        if name:
                            base[name.lower()] = price
            except Exception:
                pass
        return base

    def _load_other_products(self) -> Dict[str, tuple[Decimal, bool]]:
        """Carrega produtos 'outros' do config: nome -> (preço, por_m2)."""
        out: Dict[str, tuple[Decimal, bool]] = {}
        import os, json
        cfg = os.path.join("config", "prices.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for o in data.get("outros", []):
                        name = str(o.get("nome", "")).strip()
                        price = Decimal(str(o.get("preco", 0)))
                        per_m2 = bool(o.get("por_m2", False))
                        if name:
                            out[name] = (price, per_m2)
            except Exception:
                return {}
        return out
    
    def get_camiseta_price(self, fabric: FabricType, sleeve: SleeveType, size: SizeType, client_type: ClientType = "normal") -> Decimal:
        """Retorna preço da camiseta"""
        key = (fabric, sleeve, size, client_type)
        return self.camiseta_prices.get(key, Decimal('0'))
    
    def get_conjunto_price(self, conjunto_type: str, sleeve: SleeveType, client_type: ClientType) -> Decimal:
        """Retorna preço do conjunto"""
        key = (conjunto_type, sleeve, client_type)
        return self.conjunto_prices.get(key, Decimal('0'))
    
    def get_visual_price(self, visual_type: str) -> Decimal:
        """Retorna preço por m² da comunicação visual"""
        return self.visual_prices.get(str(visual_type).lower(), Decimal('0'))
    
    def get_short_price(self, client_type: ClientType = "normal") -> Decimal:
        """Retorna preço base do short"""
        return Decimal('25.00')  # Preço fixo base

    def get_visual_names(self) -> List[str]:
        return list(self.visual_prices.keys())

    def get_other_products(self) -> List[tuple[str, Decimal, bool]]:
        return [(name, price, per_m2) for name, (price, per_m2) in self.other_products.items()]

    def get_other_info(self, name: str) -> tuple[Decimal, bool]:
        return self.other_products.get(name, (Decimal('0'), False))
