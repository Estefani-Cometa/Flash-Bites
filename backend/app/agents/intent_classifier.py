import re
import unicodedata
from dataclasses import dataclass

from rapidfuzz import fuzz, process


@dataclass
class IntentResult:
    intent: str
    product: dict | None = None
    quantity: int | None = None
    quantity_explicit: bool = False
    plural_product: bool = False


class IntentClassifier:

    purchase_phrases = (
        "quiero",
        "dame",
        "me gustaria",
        "voy a pedir",
        "agregame",
        "anademe",
        "pideme",
        "se me antoja",
        "me provoca",
        "quisiera",
        "me llevo",
        "ponme",
        "regalame",
        "comprar",
        "pedido",
    )
    quantity_words = {
        "un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3,
        "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
        "ocho": 8, "nueve": 9, "diez": 10,
    }

    @staticmethod
    def _normalize(value: str) -> str:
        value = unicodedata.normalize("NFKD", value)
        value = "".join(char for char in value if not unicodedata.combining(char))
        return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value.lower())).strip()

    @classmethod
    def _purchase_match(cls, text: str) -> bool:
        return any(phrase in text for phrase in cls.purchase_phrases)

    @classmethod
    def _quantity(cls, text: str) -> tuple[int | None, bool]:
        for word, value in cls.quantity_words.items():
            if re.search(rf"\b{word}\b", text):
                return value, True
        match = re.search(r"\b(\d{1,2})\b", text)
        return (int(match.group(1)), True) if match else (None, False)

    @classmethod
    def _match_catalog_product(cls, text: str, products: list[dict]) -> tuple[dict | None, bool]:
        normalized_text = cls._normalize(text)
        names = {cls._normalize(product["nombre"]): product for product in products}
        for name, product in names.items():
            singular = name[:-1] if name.endswith("s") else name
            if name in normalized_text or singular in normalized_text:
                return product, bool(re.search(rf"\b{re.escape(name)}\b", normalized_text) is None)

        words = [word for word in normalized_text.split() if word not in {"quiero", "dame", "una", "un", "me", "gustaria", "de", "la", "el", "por", "favor"}]
        candidate = " ".join(words)
        token_matches = []
        for name, product in names.items():
            product_tokens = name.split()
            score = max(
                fuzz.ratio(word, product_token)
                for word in words
                for product_token in product_tokens
            ) if words else 0
            if score >= 85:
                token_matches.append((score, product, name))
        if token_matches:
            best_score = max(match[0] for match in token_matches)
            for score, product, name in token_matches:
                if score == best_score:
                    plural = any(
                        token.endswith("s") and token[:-1] in name.split()
                        for token in normalized_text.split()
                    )
                    return product, plural

        match = process.extractOne(candidate, names.keys(), scorer=fuzz.token_set_ratio)
        if match and match[1] >= 60:
            product_tokens = set(match[0].split())
            plural = any(
                token.endswith("s") and token[:-1] in product_tokens
                for token in normalized_text.split()
            )
            return names[match[0]], plural
        return None, False

    @classmethod
    def analyze(cls, message: str, products: list[dict] | None = None) -> IntentResult:
        text = cls._normalize(message)
        products = products or []
        quantity, explicit = cls._quantity(text)
        if any(word in text for word in ("elimina", "eliminar", "quita", "quitar", "borra", "borrar")):
            return IntentResult("remove_from_cart")
        if any(word in text for word in ("vacia", "vaciar", "limpia", "limpiar")) and any(word in text for word in ("carrito", "pedido", "todo")):
            return IntentResult("clear_cart")
        if cls._purchase_match(text):
            product, plural = cls._match_catalog_product(text, products)
            if product:
                return IntentResult("add_to_cart", product, quantity, explicit, plural)
            return IntentResult("product_unavailable")
        if any(word in text for word in ("menu", "producto", "productos", "precio")):
            return IntentResult("products")
        if any(word in text for word in ("horario", "hora", "abren", "cierran")):
            return IntentResult("schedule")
        if any(word in text for word in ("hola", "buenas", "buenos dias", "buenas tardes", "buenas noches")):
            return IntentResult("greeting")
        return IntentResult("rag")

    @classmethod
    def classify(cls, message: str, products: list[dict] | None = None) -> str:
        return cls.analyze(message, products).intent