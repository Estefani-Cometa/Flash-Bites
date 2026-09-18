tests = [
    "Quiero dos Hamburguesa BBQ",
    "Ver carrito",
    "Agregar una Coca-Cola 400 ml",
    "Quitar Hamburguesa BBQ",
    "Vaciar carrito",
    "Ver carrito",
    "Quiero tres Perro Caliente",
    "Quiero dos Hamburguesa Doble",
    "Qué productos tienen",
    "Cuál es el horario",
]

if __name__ == '__main__':
    try:
        from app.agents.ai_agent import agent
    except Exception as e:
        print('ERROR importing agent:', e)
        raise

    for t in tests:
        try:
            print('---')
            print('INPUT:', t)
            out = agent.chat(t)
            print('OUTPUT:', out)
        except Exception as e:
            print('ERROR running test', t, e)
            raise
