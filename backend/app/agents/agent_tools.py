from collections.abc import Callable

from langchain_core.tools import tool

from app.cart.shopping_cart import shopping_cart
from app.services.product_service import product_service
from app.services.rag_service import rag_service


def build_tools_for(
    tenant_id: int,
    customer_id: int,
    tool_log: Callable[[str], None] | None = None,
):
    def log(name: str) -> None:
        if tool_log:
            tool_log(name)

    @tool
    def agregar_al_carrito(producto: str, cantidad: int) -> str:
        """Agrega un producto real del menu al carrito del cliente actual."""
        log("agregar_al_carrito")
        if cantidad <= 0:
            return "La cantidad debe ser un entero positivo."
        product = product_service.find_best_product(producto)
        if not product:
            return "Producto no encontrado en el catalogo."
        shopping_cart.add_product(tenant_id, customer_id, product, cantidad)
        return f"Agregado: {cantidad} x {product['nombre']}. Precio unitario: ${product['precio']}."

    @tool
    def eliminar_del_carrito(producto: str) -> str:
        """Elimina un producto real del carrito del cliente actual."""
        log("eliminar_del_carrito")
        product = product_service.find_best_product(producto)
        if not product:
            return "Producto no encontrado en el catalogo."
        if shopping_cart.remove_product(tenant_id, customer_id, product["id"]):
            return f"Eliminado del carrito: {product['nombre']}."
        return f"El producto {product['nombre']} no esta en el carrito."

    @tool
    def vaciar_carrito() -> str:
        """Vacía completamente el carrito del cliente actual."""
        log("vaciar_carrito")
        shopping_cart.clear(tenant_id, customer_id)
        return "El carrito fue vaciado."

    @tool
    def ver_carrito() -> str:
        """Muestra el contenido real del carrito del cliente actual."""
        log("ver_carrito")
        return shopping_cart.summary(tenant_id, customer_id)

    @tool
    def buscar_en_menu(consulta: str) -> str:
        """Busca productos y precios reales del menu del tenant actual."""
        log("buscar_en_menu")
        products = product_service.search(consulta)
        if not products:
            return "No encontre ese producto en el catalogo del tenant."
        return "\n".join(
            f"{product['nombre']}: ${product['precio']} - {product['descripcion']}"
            for product in products[:5]
        )

    @tool
    def info_negocio(tipo: str) -> str:
        """Consulta informacion real del negocio mediante RAG del tenant actual."""
        log("info_negocio")
        documents = rag_service.search(tipo, tenant_id=tenant_id)
        if not documents:
            return "No hay informacion disponible para esa consulta en el tenant actual."
        return "\n".join(document.page_content.strip() for document in documents)

    return [
        agregar_al_carrito,
        eliminar_del_carrito,
        vaciar_carrito,
        ver_carrito,
        buscar_en_menu,
        info_negocio,
    ]
