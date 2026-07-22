import csv
from pathlib import Path

from app.core.config import settings


class ProductService:

    def __init__(self):

        self.file = Path(settings.documents_directory) / "productos.csv"

        self.products = []

        self.load_products()

    # --------------------------------------------

    def load_products(self):

        self.products = []

        if not self.file.exists():
            print("❌ No se encontró productos.csv")
            return

        with open(self.file, encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                self.products.append(
                    {
                        "id": row["id"],
                        "nombre": row["nombre"],
                        "descripcion": row["descripcion"],
                        "precio": int(row["precio"]),
                        "categoria": row["categoria"],
                    }
                )

        print(f"✅ Productos cargados: {len(self.products)}")

    # --------------------------------------------

    def get_all(self):

        return self.products

    # --------------------------------------------

    def search(self, text):

        text = text.lower()

        resultados = []

        for producto in self.products:

            contenido = (
                producto["nombre"]
                + " "
                + producto["descripcion"]
                + " "
                + producto["categoria"]
            ).lower()

            if text in contenido:
                resultados.append(producto)

        return resultados


product_service = ProductService()