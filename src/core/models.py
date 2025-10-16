from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional, Literal, Tuple

Gender = Literal["feminino", "masculino", "infantil"]
Sleeve = Literal["curta", "longa"]
Size = Literal["PP", "P", "M", "G", "GG", "XG"]
Fabric = Literal["helanca", "dryfit", "dryfit_colmeia"]
Neck = Literal["careca", "gola_v", "gola_transpassada"]


@dataclass
class OrderInfo:
	client_name: str
	order_date: date
	delivery_date: date
	description: str = ""
	fabric: Fabric = "helanca"
	neck: Neck = "careca"
	is_set: bool = False
	front_image_path: Optional[str] = None
	back_image_path: Optional[str] = None


SizeTableKey = Tuple[Gender, Size, Sleeve]


@dataclass
class SizeTable:
	quantities: Dict[SizeTableKey, int] = field(default_factory=dict)

	def set_quantity(self, gender: Gender, size: Size, sleeve: Sleeve, qty: int) -> None:
		self.quantities[(gender, size, sleeve)] = max(0, int(qty))

	def get_quantity(self, gender: Gender, size: Size, sleeve: Sleeve) -> int:
		return self.quantities.get((gender, size, sleeve), 0)

	def total(self) -> int:
		return sum(self.quantities.values())
