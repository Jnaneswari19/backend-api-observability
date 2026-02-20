from api.src.models.product import Product

class ProductService:
    def __init__(self):
        self.products = []

    def add_product(self, name, description, price):
        product = Product(name, description, price)
        self.products.append(product)
        return product.to_dict()

    def get_all_products(self):
        return [p.to_dict() for p in self.products]
