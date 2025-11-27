from typing import TypedDict


class ProductCategory(TypedDict):
    name: str
    products: list[str]


product_categories: list[ProductCategory] = [
    {
        "name": "1. Het versterken van de onderneming",
        "products": ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9"],
    },
    {
        "name": "2. Hulp bij juridische vraagstukken gerelateerd aan het ondernemerschap",
        "products": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10", "2.11"],
    },
    {
        "name": "3. Hulp bij administratie en/of financiële vraagstukken",
        "products": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9"],
    },
    {"name": "4. Trainingen en cursussen", "products": ["4.1", "4.2", "4.3"]},
    {"name": "5. Innovatie en duurzaamheid", "products": []},
    {
        "name": "6. Transitie naar een baan in loondienst (ander werk of stoppen met ondernemen)",
        "products": [],
    },
]
