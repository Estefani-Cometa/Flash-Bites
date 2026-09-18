# Documentación de la estructura actual del proyecto

## 1. Visión general

Flash-Bites es una aplicación orientada a pequeños negocios que combina un frontend web con un backend en FastAPI y un agente de IA para atender clientes en lenguaje natural. La idea principal es permitir que un negocio pueda:

- listar productos y precios reales,
- crear pedidos y clientes,
- consultar información del negocio mediante RAG,
- manejar un carrito de compras persistente,
- interactuar con un chatbot que responde como un vendedor asistente.

La arquitectura actual está pensada para funcionar como MVP funcional, con soporte para multi-tenant, almacenamiento en base de datos local o PostgreSQL, y una capa de IA con herramientas reales para consultar catálogo, carrito e información del negocio.

---

## 2. Arquitectura general

El proyecto está dividido en dos grandes partes:

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- Inteligencia artificial: LangGraph + Gemini + tools
- Recuperación documental: Chroma + documentos CSV/TXT/PDF
- Orquestación: Docker + Docker Compose

Flujo general:

1. El usuario entra a la interfaz web.
2. El frontend usa Axios para comunicarse con la API.
3. La API valida autenticación y expone rutas REST.
4. El backend consulta la base de datos y servicios del negocio.
5. El agente de IA procesa mensajes del usuario usando tools reales.
6. La respuesta se devuelve al frontend y se muestra en el chat.

---

## 3. Estructura del repositorio

### 3.1 Raíz del proyecto

- `README.md`: documentación general y comandos rápidos.
- `docker-compose.yml`: levanta backend, PostgreSQL y frontend.
- `DEPLOYMENT.md`: guía de despliegue y configuración de producción.
- `QUICKSTART.md`: pasos rápidos para arrancar la app.
- `backend/`: aplicación principal del servidor.
- `frontend/`: cliente web.
- `docs/`: documentación complementaria.

### 3.2 Backend

La carpeta principal de la lógica de negocio es `backend/app`:

- `main.py`: inicializa la aplicación FastAPI, middlewares y routers.
- `db.py`: configuración y conexión a la base de datos.
- `db_models.py`: modelos SQLAlchemy para tenants, clientes, productos, órdenes y conversaciones.
- `core/config.py`: configuración global por variables de entorno.
- `api/routes/`: endpoints REST por módulo.
- `services/`: servicios de negocio, catálogo, búsqueda y RAG.
- `agents/`: lógica del agente conversacional.
- `cart/`: lógica del carrito persistente.
- `models/`: esquemas Pydantic para request/response.

### 3.3 Frontend

La app web está en `frontend/src`:

- `main.jsx`: punto de entrada de React.
- `App.jsx`: interfaz principal con chat, producto y acciones rápidas.
- `index.css`: estilos globales y Tailwind.

---

## 4. Cómo funciona la capa de backend

### 4.1 Inicialización de la aplicación

La aplicación se inicia desde `backend/app/main.py`.

Allí se hace lo siguiente:

- crea una instancia de FastAPI,
- habilita CORS a partir de `ALLOWED_ORIGINS`,
- registra cada router principal:
  - `/api/v1/auth`
  - `/api/v1/products`
  - `/api/v1/customers`
  - `/api/v1/orders`
  - `/api/v1/billing`
  - `/api/v1/chat`
  - `/api/v1/health`
- ejecuta `initialize_database()` para crear las tablas si no existen,
- importa productos del CSV al iniciar si el catálogo está vacío.

Esto deja la app lista para operar con una base de datos funcional y datos iniciales del negocio.

### 4.2 Configuración y entorno

La configuración central vive en `backend/app/core/config.py`.

Aquí se definen variables como:

- `APP_NAME`
- `API_V1_PREFIX`
- `DATABASE_URL`
- `TENANT_ID`
- `BUSINESS_NAME`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `ALLOWED_ORIGINS`
- `CHROMA_PERSIST_DIRECTORY`
- `DOCUMENTS_DIRECTORY`

Esto hace que la app pueda cambiar de entorno sin tocar código, usando `.env` o variables del entorno.

### 4.3 Base de datos y modelos

La persistencia se define en `backend/app/db_models.py`.

Los modelos principales son:

- `Tenant`: negocio / tenant actual
- `Product`: catálogo de productos
- `Customer`: clientes del negocio
- `Order`: pedidos realizados
- `Conversation`: historial y carrito por cliente
- `TenantDocument`: documentos del negocio para RAG

La estructura está preparada para un modelo multi-tenant, donde cada negocio puede tener sus propios productos, clientes y conversaciones.

### 4.4 Conexión a la base de datos

En `backend/app/db.py` se crea el engine SQLAlchemy y la sesión para SQLite o PostgreSQL.

Funciones clave:

- `normalize_database_url()`: normaliza URLs de PostgreSQL para que el driver correcto funcione.
- `get_db()`: genera sesiones para endpoints.
- `initialize_database()`: crea schema y registra el tenant principal si no existe.

Esto hace que el backend sea compatible con varios motores sin cambiar demasiado la lógica del dominio.

---

## 5. Servicios implementados

### 5.1 `ProductService`

Archivo: `backend/app/services/product_service.py`

Este servicio hace varias cosas importantes:

- importa productos desde `documents/productos.csv` si la base está vacía,
- normaliza texto para búsquedas de productos,
- calcula similitud usando token overlap y comparación difusa,
- busca productos por coincidencia parcial de nombre/descripción,
- devuelve el mejor resultado para una consulta.

Este servicio mejora la experiencia porque el agente no necesita depender de una búsqueda exacta. Si el usuario dice algo parecido a “hamburguesa”, “papitas”, “queso”, etc., el sistema intenta encontrar la mejor coincidencia real.

### 5.2 `BusinessService`

Archivo: `backend/app/services/business_service.py`

Este servicio encapsula la lógica de negocio:

- listar productos en formato para API,
- registrar clientes,
- crear o recuperar clientes por `user_id`,
- obtener el nombre de un cliente para personalizar la conversación,
- crear pedidos con validación de cantidad y producto,
- listar pedidos del usuario autenticado.

También centraliza validaciones y ayuda a prevenir errores de negocio.

### 5.3 `RAGService`

Archivo: `backend/app/services/rag_service.py`

Este servicio carga documentos del directorio `documents/` y los indexa en Chroma para búsqueda semántica.

Soporta:

- `.txt`
- `.csv`
- `.pdf`

Con embeddings de Gemini y un splitter de texto. Luego permite hacer consultas tipo:

- horarios,
- información del negocio,
- políticas,
- servicios,
- promociones o detalles operativos.

Esto permite que el agente responda con información real del negocio en vez de inventar contenido.

### 5.4 `ShoppingCart`

Archivo: `backend/app/cart/shopping_cart.py`

El carrito está persistido dentro de la entidad `Conversation`, no solo en memoria.

Funcionalidades:

- agregar producto,
- eliminar producto,
- vaciar carrito,
- consultar carrito,
- calcular subtotal y total,
- resumir el pedido actual.

Esto mejora significativamente el flujo del agente porque el carrito no se pierde entre mensajes ni llamadas del cliente.

---

## 6. Cómo funcionan los endpoints principales

### 6.1 `auth`

Ruta: `/api/v1/auth/register`

- recibe email, password y full_name,
- genera un JWT con `create_access_token`,
- devuelve un token para autenticar al usuario.

Actualmente la autenticación es funcional como MVP y se usa en front para crear una cuenta demo.

### 6.2 `products`

Ruta: `/api/v1/products`

- devuelve el catálogo de productos disponibles,
- se serializa con Pydantic,
- el frontend carga esos productos para mostrarlos y crear pedidos demo.

### 6.3 `customers`

Ruta: `/api/v1/customers`

- permite registrar clientes del negocio,
- se usa para asociar pedidos a personas concretas.

### 6.4 `orders`

Ruta: `/api/v1/orders`

- crea un pedido con items y customer_id,
- valida que el cliente pertenezca al usuario autenticado,
- calcula el total con base en precios del catálogo.

### 6.5 `chat`

Ruta: `/api/v1/chat`

Es el punto más importante de la experiencia de IA.

Flujo:

1. El frontend envía `{ "message": "..." }`.
2. El backend valida que el mensaje no venga vacío.
3. Obtiene o crea un customer asociado al email del usuario autenticado.
4. Crea un `IncomingMessage` con tenant, customer, canal y texto.
5. Llama a `agent.process_message()`.
6. El agente responde en texto natural.

### 6.6 `health`

Ruta: `/api/v1/health`

Sirve para verificar que la API esté levantada y funcionando.

---

## 7. Cómo funciona el agente de IA

Archivo principal: `backend/app/agents/ai_agent.py`

### 7.1 Objetivo

El agente actúa como asistente vendedor del negocio, usando herramientas reales para responder consultas sobre catálogo, carrito y negocio.

### 7.2 Prompt del sistema

El `SYSTEM_PROMPT` define reglas estrictas:

- habla en español,
- responde como un vendedor profesional,
- responde solo sobre el tenant actual,
- usa herramientas para consultar información real,
- no inventa precios ni productos,
- si no sabe, lo dice con honestidad,
- si la consulta no es del negocio, redirige amablemente,
- usa carrito y catálogo reales.

Esto ayuda a reducir alucinaciones de IA.

### 7.3 Checkpointer

El agente usa `MemorySaver` o `PostgresSaver` según el backend configurado.

- Si la base es PostgreSQL, intenta usar `langgraph.checkpoint.postgres.PostgresSaver`.
- Si no puede, se cae a memoria local (`MemorySaver`).

Esto permite mantener contexto y continuidad de conversación.

### 7.4 Herramientas del agente

Archivo: `backend/app/agents/agent_tools.py`

El agente tiene herramientas como:

- `agregar_al_carrito(producto, cantidad)`: agrega producto real al carrito.
- `eliminar_del_carrito(producto)`: elimina un producto del carrito.
- `vaciar_carrito()`: limpia el carrito.
- `ver_carrito()`: muestra el estado actual.
- `buscar_en_menu(consulta)`: busca productos por texto.
- `info_negocio(tipo)`: consulta información del negocio con RAG.

Estas herramientas convierten la IA en un asistente accionable, no solo conversacional.

### 7.5 Reglas de interacción con nombres

Cuando un usuario escribe un nombre, el agente intenta detectar si es un nombre y almacenarlo asociando al cliente.

Esto mejora la personalización del diálogo en futuras respuestas.

---

## 8. Cómo funciona el flujo de chat completo

El flujo real de interacción es el siguiente:

1. El usuario escribe un mensaje desde el frontend.
2. El frontend revisa si hay token guardado en localStorage.
3. Si no existe, crea una cuenta demo.
4. El frontend llama a `POST /api/v1/chat`.
5. El backend valida el mensaje.
6. Busca o crea al cliente según el email del usuario.
7. Crea un `IncomingMessage`.
8. `BusinessAIAgent.process_message()` toma ese mensaje.
9. El agente identifica al cliente y revisa el nombre conocido.
10. Se construye un grafo LangGraph con herramientas.
11. El modelo Gemini responde usando las tools.
12. El agente puede consultar producto, carrito o información del negocio.
13. La respuesta final se devuelve al frontend como `{ "reply": "..." }`.
14. El frontend agrega el mensaje del asistente al historial.

Este flujo convierte la app en una experiencia de soporte comercial intelligentemente automatizada.

---

## 9. Cómo funciona el frontend

Archivo principal: `frontend/src/App.jsx`

El frontend tiene una interfaz muy simple pero funcional:

- estado para token,
- lista de productos,
- historial de chat,
- input de usuario,
- resumen del pedido.

### 9.1 Cuenta demo

Al iniciar, si no hay token guardado, el usuario puede crear una cuenta demo con:

- email: `demo@business.com`
- password: `demo1234`
- nombre: `Demo Owner`

La cuenta se guarda en `localStorage` para reutilizar sesión.

### 9.2 Carga de productos

Al montar la app, hace una petición a `/products` para visualizarlos.

### 9.3 Envío de mensajes

Cuando el usuario escribe y presiona Enter o el botón, la app:

- verifica que haya contenido,
- crea cuenta si no existe,
- envía el mensaje a `/chat`,
- recibe la respuesta y la agrega al historial.

### 9.4 Pedido demo

La app también permite crear un pedido simple con un producto disponible, usando:

- un cliente demo,
- un item de orden,
- la API `/orders`.

Esto sirve para demostrar el flujo completo de negocio sin requerir UI compleja.

---

## 10. Mejoras implementadas respecto a una base más básica

La estructura actual ya incluye varias mejoras relevantes con respecto a un MVP simple:

### 10.1 Multi-tenant preparado

- existe un modelo `Tenant`,
- cada producto, cliente y pedido está asociado a un tenant,
- la lógica de negocio filtra por tenant actual.

Esto permite escalar la app a más de un negocio sin mezclar datos.

### 10.2 Agente con herramientas reales

En vez de responder solo texto estático, el agente consulta:

- catálogo,
- carrito,
- información del negocio.

Esto mejora mucho la utilidad real del asistente.

### 10.3 RAG para información del negocio

La app puede leer documentos y responder con datos reales del negocio.

Esto reduce la probabilidad de respuestas inventadas y aumenta la confiabilidad.

### 10.4 Carrito persistente

El carrito ya no vive solo en memoria. Se guarda en conversaciones con JSON, por lo que puede ser usado a lo largo de una sesión.

### 10.5 Búsqueda inteligente de productos

La lógica de `ProductService` usa normalización, stop words, overlap y similitud fuzzy para manejar consultas no exactas.

Eso hace que el buscador sea más natural para usuarios reales.

### 10.6 Manejo de contexto del cliente

El agente intenta recordar el nombre y personalizar la experiencia sin hacer repetir preguntas innecesarias.

### 10.7 Compatibilidad con SQLite y PostgreSQL

El backend prepara conexiones para ambos motores, lo cual facilita desarrollo local y despliegue en producción.

### 10.8 Dockerización

El proyecto tiene contenedores para:

- backend,
- frontend,
- PostgreSQL.

Esto hace más rápido el arranque en entornos homogéneos.

### 10.9 Capa de seguridad básica

- se usa JWT,
- CORS está habilitado,
- el acceso a endpoints protegidos se valida con dependencia de usuario.

---

## 11. Puntos de integración importantes

El backend está conectado por varias capas:

- `routes` -> `services`
- `services` -> `db_models` / `SessionLocal`
- `agents` -> `services` + `shopping_cart` + `rag_service`
- `frontend` -> `API REST` -> `backend`

Esto crea un flujo limpio de responsabilidades:

- rutas: entrada HTTP,
- servicios: lógica del negocio,
- modelos: persistencia,
- agentes: conversación e IA,
- frontend: experiencia visual.

---

## 12. Estado actual del proyecto

La estructura actual está funcionando como un MVP funcional con enfoque comercial y de demostración. Incluye:

- ventas básicas,
- catálogo y productos,
- clientes,
- pedidos,
- chatbot IA,
- empresa y documentos del negocio,
- almacenamiento persistente,
- despliegue preparado para producción.

La arquitectura está bien organizada para continuar creciendo con nuevos módulos como:

- pagos,
- inventario,
- facturación,
- CRM,
- administración dashboard,
- autenticación real con usuarios,
- más documentos y más proveedores de IA.

---

## 13. Resumen corto

En pocas palabras, la app funciona así:

- el frontend presenta la experiencia de negocio,
- el backend expone la lógica y la persistencia,
- el agente de IA usa herramientas para manejar catálogo, carrito e información del negocio,
- la base de datos guarda clientes, órdenes y conversaciones,
- el RAG complementa la IA con información documentada del negocio,
- el sistema está preparado para crecer con un enfoque real de negocio digital.

---

## 14. Archivos clave para revisar

- [backend/app/main.py](../backend/app/main.py)
- [backend/app/db.py](../backend/app/db.py)
- [backend/app/db_models.py](../backend/app/db_models.py)
- [backend/app/services/business_service.py](../backend/app/services/business_service.py)
- [backend/app/services/product_service.py](../backend/app/services/product_service.py)
- [backend/app/services/rag_service.py](../backend/app/services/rag_service.py)
- [backend/app/cart/shopping_cart.py](../backend/app/cart/shopping_cart.py)
- [backend/app/agents/ai_agent.py](../backend/app/agents/ai_agent.py)
- [backend/app/agents/agent_tools.py](../backend/app/agents/agent_tools.py)
- [frontend/src/App.jsx](../frontend/src/App.jsx)
- [docker-compose.yml](../docker-compose.yml)
