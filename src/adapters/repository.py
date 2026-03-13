"""Repository Adapter"""

from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort


class InMemoryRepository(RepositoryPort):

    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.movements: List[Movement] = []

    def save_product(self, product: Product) -> None:
        self.products[product.id] = product

    def load_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def load_all_products(self) -> Dict[str, Product]:
        return self.products.copy()

    def delete_product(self, product_id: str) -> None:
        if product_id in self.products:
            del self.products[product_id]

    def save_movement(self, movement: Movement) -> None:
        self.movements.append(movement)

    def load_movements(self) -> List[Movement]:
        return self.movements.copy()


class RepositoryFactory:

    @staticmethod
    def create_repository(repository_type: str = "memory"):

        if repository_type == "memory":
            return InMemoryRepository()

        raise ValueError("Unbekannter Repository Typ")