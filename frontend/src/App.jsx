import { useEffect, useState } from "react";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [products, setProducts] = useState([]);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hola 👋 ¿En qué puedo ayudarte hoy?",
    },
  ]);
  const [input, setInput] = useState("");
  const [orderSummary, setOrderSummary] = useState("");

  // Configurar token al iniciar
  useEffect(() => {
    const savedToken = localStorage.getItem("token");

    if (savedToken) {
      setToken(savedToken);
      api.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${savedToken}`;
    }
  }, []);

  // Cargar productos
  useEffect(() => {
    api
      .get("/products")
      .then((res) => setProducts(res.data.items))
      .catch((err) => console.error(err));
  }, []);

  // Registrar cuenta demo
  const registerDemoAccount = async () => {
    try {
      const res = await api.post("/auth/register", {
        email: "demo@business.com",
        password: "demo123",
        full_name: "Demo Owner",
      });

      const newToken = res.data.token;

      setToken(newToken);

      localStorage.setItem("token", newToken);

      api.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${newToken}`;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "✅ Cuenta demo creada correctamente.",
        },
      ]);

      return newToken;
    } catch (error) {
      console.log(error);

      // Si el usuario ya existe,
      // intenta usar el token guardado

      const savedToken = localStorage.getItem("token");

      if (savedToken) {
        setToken(savedToken);

        api.defaults.headers.common[
          "Authorization"
        ] = `Bearer ${savedToken}`;

        return savedToken;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠ No fue posible crear la cuenta demo.",
        },
      ]);

      return null;
    }
  };

  // Enviar mensaje al chat
  const sendMessage = async () => {
    if (!input.trim()) return;

    let currentToken = token;

    if (!currentToken) {
      currentToken = await registerDemoAccount();

      if (!currentToken) return;
    }

    const currentMessage = input;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: currentMessage,
      },
    ]);

    setInput("");

    try {
      const res = await api.post("/chat", {
        message: currentMessage,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.reply,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "❌ Error al comunicarse con el servidor.",
        },
      ]);
    }
  };

  // Crear pedido
  const createDemoOrder = async () => {
    let currentToken = token;

    if (!currentToken) {
      currentToken = await registerDemoAccount();

      if (!currentToken) return;
    }

    try {
      const res = await api.post("/orders", {
        customer_id: "cust-1",
        items: [
          {
            product_id: "prod-1",
            quantity: 2,
          },
        ],
      });

      setOrderSummary(
        `✅ Pedido ${res.data.id} creado correctamente. Total: $${res.data.total}`
      );
    } catch (error) {
      console.error(error);

      setOrderSummary(
        "❌ No fue posible crear el pedido."
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
          <h1 className="text-3xl font-semibold">
            Business AI Agent
          </h1>

          <p className="mt-2 text-slate-400">
            Asistente inteligente para pequeños negocios.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-medium">
                Chat del Agente
              </h2>

              <button
                onClick={registerDemoAccount}
                className="rounded-lg bg-cyan-600 px-3 py-2"
              >
                Activar Demo
              </button>
            </div>

            <div className="flex h-96 flex-col gap-3 overflow-y-auto rounded-xl bg-slate-950/60 p-3">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "ml-auto bg-cyan-600"
                      : "bg-slate-800"
                  }`}
                >
                  {message.content}
                </div>
              ))}
            </div>

            <div className="mt-4 flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && sendMessage()
                }
                placeholder="Pregunta algo..."
                className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2"
              />

              <button
                onClick={sendMessage}
                className="rounded-xl bg-cyan-600 px-4 py-2"
              >
                Enviar
              </button>
            </div>
          </section>

          <aside className="flex flex-col gap-6">
            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl">
              <h2 className="mb-3 text-xl font-medium">
                Productos
              </h2>

              <div className="space-y-2">
                {products.map((product) => (
                  <div
                    key={product.id}
                    className="rounded-xl border border-slate-800 bg-slate-950/60 p-3"
                  >
                    <div className="font-medium">
                      {product.name}
                    </div>

                    <div className="text-sm text-slate-400">
                      {product.description}
                    </div>

                    <div className="text-cyan-400">
                      ${product.price}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 shadow-xl">
              <h2 className="mb-3 text-xl font-medium">
                Acciones rápidas
              </h2>

              <button
                onClick={createDemoOrder}
                className="w-full rounded-xl bg-emerald-600 px-3 py-2"
              >
                Crear pedido demo
              </button>

              {orderSummary && (
                <p className="mt-3 text-sm text-emerald-400">
                  {orderSummary}
                </p>
              )}
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default App;
