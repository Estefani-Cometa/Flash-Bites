import csv
import logging
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from app.core.config import settings
from app.db import SessionLocal
from app.db_models import Product

logger = logging.getLogger(__name__)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        ch for ch in normalized if not unicodedata.combining(ch)
    )
    normalized = normalized.lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_token(token: str) -> str:
    token = normalize_text(token)
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


STOP_WORDS = {
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "unos",
    "unas",
    "de",
    "del",
    "para",
    "por",
    "con",
    "sin",
    "en",
    "al",
    "a",
    "y",
    "o",
    "que",
    "lo",
    "se",
    "mi",
    "tu",
    "su",
    "sus",
    "quiero",
    "deseo",
    "necesito",
    "agregar",
    "añadir",
    "pedir",
    "ordenar",
    "llevar",
    "quieres",
    "quiera",
    "puedo",
    "por",
    "favor",
}


def extract_tokens(text: str) -> set[str]:
    return {
        normalize_token(token)
        for token in normalize_text(text).split()
        if token
    }


def filter_query_tokens(tokens: set[str]) -> set[str]:
    return {token for token in tokens if token not in STOP_WORDS}


def token_overlap_score(query_tokens: set[str], target_tokens: set[str]) -> float:
    if not query_tokens or not target_tokens:
        return 0.0

    intersection = query_tokens & target_tokens
    if not intersection:
        return 0.0

    query_ratio = len(intersection) / len(query_tokens)
    target_ratio = len(intersection) / len(target_tokens)
    return (query_ratio + target_ratio) / 2


def similarity_ratio(source: str, target: str) -> float:
    return SequenceMatcher(
        None,
        normalize_text(source),
        normalize_text(target),
    ).ratio()


class ProductService:

    def __init__(self):
        self.file = Path(settings.documents_directory) / "productos.csv"

    def import_from_csv_if_empty(self) -> None:
        with SessionLocal.begin() as db:
            if db.query(Product).filter(Product.tenant_id == settings.tenant_id).first():
                return

            if not self.file.exists():
                logger.warning("productos.csv no encontrado en %s", self.file)
                return

            with open(self.file, encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    db.add(
                        Product(
                            id=int(row["id"].strip()),
                            tenant_id=settings.tenant_id,
                            nombre=row["nombre"].strip(),
                            descripcion=row["descripcion"].strip(),
                            precio=int(row["precio"].strip()),
                            disponible=True,
                        )
                    )

            logger.info("Catálogo importado para tenant %d", settings.tenant_id)

    # --------------------------------------------

    def get_all(self) -> list[dict]:
        with SessionLocal() as db:
            products = (
                db.query(Product)
                .filter(
                    Product.tenant_id == settings.tenant_id,
                    Product.disponible.is_(True),
                )
                .order_by(Product.id)
                .all()
            )
            return [
                {
                    "id": product.id,
                    "nombre": product.nombre,
                    "descripcion": product.descripcion,
                    "ingredientes": "",
                    "precio": product.precio,
                    "categoria": "",
                }
                for product in products
            ]

    # --------------------------------------------

    def _score_product(self, text: str, producto: dict) -> float:
        query_tokens = filter_query_tokens(extract_tokens(text))
        if not query_tokens:
            return 0.0

        name_tokens = extract_tokens(producto["nombre"])
        description_tokens = extract_tokens(producto.get("descripcion", ""))
        category_tokens = extract_tokens(producto.get("categoria", ""))
        ingredient_tokens = extract_tokens(producto.get("ingredientes", ""))

        all_tokens = (
            name_tokens
            | description_tokens
            | category_tokens
            | ingredient_tokens
        )

        intersection = query_tokens & all_tokens
        if not intersection:
            return 0.0

        if len(query_tokens) > 1 and query_tokens <= name_tokens:
            return 1.0

        if len(query_tokens) == 1 and len(name_tokens) > 1:
            return 0.0

        query_cover = len(intersection) / len(query_tokens)
        target_cover = len(intersection) / len(all_tokens)
        content_score = 0.7 * query_cover + 0.3 * target_cover

        name_score = token_overlap_score(query_tokens, name_tokens)
        name_similarity = similarity_ratio(text, producto["nombre"])
        description_similarity = similarity_ratio(
            text,
            producto.get("descripcion", ""),
        )
        similarity_score = max(name_similarity * 0.8, description_similarity * 0.4)

        return max(name_score, content_score, similarity_score)

    # --------------------------------------------

    def search(self, text: str) -> list[dict]:
        products = self.get_all()
        text = text.strip()
        if not text:
            return []

        scored_products: list[tuple[float, dict]] = []

        for producto in products:
            score = self._score_product(text, producto)
            if score > 0.0:
                scored_products.append((score, producto))

        if not scored_products:
            normalized_query = normalize_text(text)
            for producto in products:
                combined = " ".join(
                    [
                        producto["nombre"],
                        producto.get("descripcion", ""),
                        producto.get("categoria", ""),
                        producto.get("ingredientes", ""),
                    ]
                )
                if normalized_query in normalize_text(combined):
                    scored_products.append((0.25, producto))

        scored_products.sort(key=lambda item: item[0], reverse=True)
        return [producto for _, producto in scored_products]

    # --------------------------------------------

    def find_best_product(self, text: str, min_score: float = 0.65) -> dict | None:
        products = self.get_all()
        if not text.strip():
            return None

        scored_products = [
            (self._score_product(text, producto), producto)
            for producto in products
        ]

        if not scored_products:
            return None

        scored_products.sort(key=lambda item: item[0], reverse=True)
        score, producto = scored_products[0]
        return producto if score >= min_score else None


product_service = ProductService()