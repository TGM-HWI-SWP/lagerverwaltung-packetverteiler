from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort


class WarehouseService:

    def __init__(self, repository: RepositoryPort):
        self.repo = repository

    def create_package(self, id, name, description, price):

        product = Product(
            id=id,
            name=name,
            description=description,
            price=price,
            quantity=1
        )

        self.repo.save_product(product)

    def register_incoming(self, product_id, amount):

        product = self.repo.load_product(product_id)

        product.update_quantity(amount)

        movement = Movement(
            id=f"M-{product_id}",
            product_id=product_id,
            product_name=product.name,
            quantity_change=amount,
            movement_type="IN",
            performed_by="scanner"
        )

        self.repo.save_movement(movement)

    def get_inventory(self):

        return self.repo.load_all_products()

    def get_movements(self):

        return self.repo.load_movements()