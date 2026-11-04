# Catálogo de productos

## Fuente única actual

`backend/documents/productos.csv` es la fuente canónica del catálogo en el MVP. El backend lo carga al iniciar mediante `ProductService`; la API, los pedidos y las respuestas de catálogo del agente consumen ese servicio. El catálogo es de solo lectura desde la aplicación y los cambios se realizan en el CSV.

La persistencia en base de datos queda para la migración definida en FB-03. Al hacerla, debe reemplazarse esta fuente sin volver a crear catálogos separados para API, pedidos o agente.

## Contrato de producto

La API devuelve `GET /api/v1/products` con un objeto `items`. Cada elemento tiene esta estructura:

```json
{
  "id": "1",
  "name": "Hamburguesa Clásica",
  "description": "Hamburguesa tradicional",
  "ingredients": "Carne de res 150 g, queso cheddar, lechuga, tomate, cebolla, salsa especial",
  "price": 18000,
  "category": "Hamburguesas"
}
```

- `id` se conserva como texto tal como aparece en la columna `id` del CSV; los pedidos envían ese mismo valor en `product_id`.
- `name`, `description`, `ingredients` y `category` son textos normalizados desde las columnas `nombre`, `descripcion`, `ingredientes` y `categoria`.
- `price` es un entero en pesos colombianos (COP), tomado de `precio`. No se convierte a una unidad monetaria diferente ni se recibe del cliente al crear pedidos.
- Los IDs deben ser únicos y cada producto debe tener un nombre. La carga del catálogo falla con un error descriptivo si faltan columnas requeridas, hay IDs duplicados o un precio no válido.

## Pedidos y agente

La creación de pedidos busca cada `product_id` en el mismo `ProductService` y calcula el total con el precio del catálogo. Un ID inexistente se rechaza con HTTP 404.

Cuando el agente presenta el menú o enumera productos para un pedido, muestra los IDs, nombres y precios cargados por ese servicio. No agregues nombres, IDs ni precios del catálogo como listas paralelas en el agente o en la API.

## Actualizar el catálogo

Al agregar o modificar un producto, actualiza `backend/documents/productos.csv` conservando sus encabezados y validando que el ID sea único y el precio un entero en COP. Revisa que la interfaz de productos y el pedido demo sigan usando el ID entregado por la API, no un ID inventado o codificado aparte.
