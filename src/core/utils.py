from datetime import date, timedelta
from typing import Iterable

# 1 cm = 28.3464567 points (PostScript)
CM_TO_PT = 28.3464567


def cm(value: float) -> float:
	"""Converte centímetros para pontos."""
	return value * CM_TO_PT


def add_business_days_including_saturday(start: date, days: int) -> date:
	"""Soma 'days' dias úteis incluindo sábado (seg=0 .. dom=6; úteis: 0..5).
	Não pula feriados (o negócio informou que normalmente trabalham em feriados).
	"""
	result = start
	added = 0
	while added < days:
		result += timedelta(days=1)
		if result.weekday() <= 5:  # 0..5 = segunda..sábado
			added += 1
	return result


def sum_iter(values: Iterable[int]) -> int:
	return sum(int(v) for v in values)
