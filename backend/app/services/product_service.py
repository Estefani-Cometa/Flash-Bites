import csv
from pathlib import Path

from app.core.config import settings


class ProductService:
    """Read the canonical product catalog from the configured CSV file."""

    REQUIRED_COLUMNS = {
        "id",
        "nombre",
        "descripcion",
        "ingredientes",
        "precio",
        "categoria",
    }

    def __init__(self) -> None:
        self.file = Path(settings.documents_directory) / "productos.csv"
        self.products: list[dict[str, str | int]] = []
        self.products_by_id: dict[str, dict[str, str | int]] = {}
        self.load_products()

    def load_products(self) -> None:
        if not self.file.is_file():
            raise FileNotFoundError(f"Product catalog not found: {self.file}")

        products: list[dict[str, str | int]] = []
        products_by_id: dict[str, dict[str, str | int]] = {}

        with self.file.open(encoding="utf-8", newline="") as catalog_file:
            reader = csv.DictReader(catalog_file)
            fieldnames = set(reader.fieldnames or [])
            missing_columns = self.REQUIRED_COLUMNS - fieldnames
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(f"Product catalog is missing columns: {missing}")

            for row_number, row in enumerate(reader, start=2):
                product_id = (row.get("id") or "").strip()
                if not product_id:
                    raise ValueError(f"Product catalog row {row_number} has no id")
                if product_id in products_by_id:
                    raise ValueError(
                        f"Product catalog contains duplicate id '{product_id}'"
                    )

                try:
                    price = int((row.get("precio") or "").strip())
                except ValueError as exc:
                    raise ValueError(
                        f"Product catalog row {row_number} has an invalid price"
                    ) from exc
                if price < 0:
                    raise ValueError(
                        f"Product catalog row {row_number} has a negative price"
                    )

                product = {
                    "id": product_id,
                    "name": (row.get("nombre") or "").strip(),
                    "description": (row.get("descripcion") or "").strip(),
                    "ingredients": (row.get("ingredientes") or "").strip(),
                    "price": price,
                    "category": (row.get("categoria") or "").strip(),
                }
                if not product["name"]:
                    raise ValueError(
                        f"Product catalog row {row_number} has no name"
                    )

                products.append(product)
                products_by_id[product_id] = product

        self.products = products
        self.products_by_id = products_by_id

    def get_all(self) -> list[dict[str, str | int]]:
        return [product.copy() for product in self.products]

    def get_by_id(self, product_id: str) -> dict[str, str | int]:
        try:
            return self.products_by_id[product_id].copy()
        except KeyError as exc:
            raise ValueError("Product not found") from exc

    def search(self, text: str) -> list[dict[str, str | int]]:
        query = text.casefold()
        searchable_fields = ("name", "description", "ingredients", "category")
        return [
            product.copy()
            for product in self.products
            if any(query in str(product[field]).casefold() for field in searchable_fields)
        ]


product_service = ProductService()
