import asyncio
from webworky.webworky import WebWorky

# Esempio di utilizzo della classe WebWorky
async def example_hook(websocket, payload):
    response = {"message": "response_example", "payload": {"status": "received", "data": payload}}
    return response

if __name__ == "__main__":
    webworky = WebWorky()
    webworky.register_hook("example_message", example_hook)
    
    # Avvio dell'event loop
    asyncio.run(webworky.start_server())