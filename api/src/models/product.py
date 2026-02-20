class Product:
    def __init__(self, name, description, price):
        self.id = id(self)  # simple unique id
        self.name = name
        self.description = description
        self.price = price

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
        }
