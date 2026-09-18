from app.agents.intent_classifier import IntentClassifier
from app.services.product_service import product_service


def test_purchase_intentions_against_catalog():
    products = product_service.get_all()
    cases = {
        "Hola": "greeting",
        "Quiero una hamburguesa": "add_to_cart",
        "Quiero hamburguesas": "add_to_cart",
        "Dame 2 salchipapas": "add_to_cart",
        "Me gustaría una pizza": "product_unavailable",
        "Cuál es el menú": "products",
        "Elimina la hamburguesa de mi pedido": "remove_from_cart",
        "Vacía mi carrito": "clear_cart",
        "Qué horario tienen": "schedule",
        "Cuál es tu color favorito": "rag",
    }

    for message, expected_intent in cases.items():
        assert IntentClassifier.analyze(message, products).intent == expected_intent


def test_purchase_quantity_and_plurality():
    products = product_service.get_all()

    one = IntentClassifier.analyze("Quiero una hamburguesa", products)
    assert one.quantity == 1
    assert one.quantity_explicit is True
    assert one.plural_product is False

    plural = IntentClassifier.analyze("Quiero hamburguesas", products)
    assert plural.quantity is None
    assert plural.quantity_explicit is False
    assert plural.plural_product is True

    two = IntentClassifier.analyze("Dame 2 salchipapas", products)
    assert two.quantity == 2
    assert two.quantity_explicit is True