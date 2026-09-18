from app.db import initialize_database
from app.services.product_service import product_service


if __name__ == "__main__":
    initialize_database()
    product_service.import_from_csv_if_empty()
    print("Catálogo importado si la tabla products estaba vacía.")
