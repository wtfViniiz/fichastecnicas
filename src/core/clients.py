from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime


@dataclass
class Client:
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Métricas simples agregadas
    total_spent: float = 0.0
    budgets_count: int = 0
    last_purchase_at: Optional[str] = None


class ClientStorage:
    """Armazena clientes em JSON com operações CRUD e métricas simples."""

    def __init__(self, storage_dir: str = "data") -> None:
        self.storage_dir = storage_dir
        self.clients_file = os.path.join(storage_dir, "clients.json")
        self._ensure_storage_dir()
        self._load()

    def _ensure_storage_dir(self) -> None:
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _load(self) -> None:
        self.clients: List[Dict[str, Any]] = []
        if os.path.exists(self.clients_file):
            try:
                with open(self.clients_file, "r", encoding="utf-8") as f:
                    self.clients = json.load(f)
            except Exception:
                self.clients = []

    def _save(self) -> None:
        try:
            with open(self.clients_file, "w", encoding="utf-8") as f:
                json.dump(self.clients, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar clientes: {e}")

    def list_clients(self) -> List[Client]:
        return [Client(**c) for c in self.clients]

    def create_client(self, name: str, phone: str, email: Optional[str] = None) -> Client:
        client_id = f"CLI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.clients)}"
        client = Client(id=client_id, name=name, phone=phone, email=email)
        self.clients.append(asdict(client))
        self._save()
        return client

    def update_client(self, client: Client) -> None:
        for i, c in enumerate(self.clients):
            if c.get("id") == client.id:
                self.clients[i] = asdict(client)
                self._save()
                return

    def delete_client(self, client_id: str) -> None:
        self.clients = [c for c in self.clients if c.get("id") != client_id]
        self._save()

    def find_by_id(self, client_id: str) -> Optional[Client]:
        for c in self.clients:
            if c.get("id") == client_id:
                return Client(**c)
        return None

    def find_by_name_or_phone(self, term: str) -> List[Client]:
        t = term.lower().strip()
        result: List[Client] = []
        for c in self.clients:
            name = (c.get("name") or "").lower()
            phone = (c.get("phone") or "").lower()
            if t in name or t in phone:
                result.append(Client(**c))
        return result

    def record_budget_metrics(self, client_id: str, budget_total: float) -> None:
        for i, c in enumerate(self.clients):
            if c.get("id") == client_id:
                c["total_spent"] = float(c.get("total_spent", 0.0)) + float(budget_total)
                c["budgets_count"] = int(c.get("budgets_count", 0)) + 1
                c["last_purchase_at"] = datetime.now().isoformat()
                self.clients[i] = c
                self._save()
                return

