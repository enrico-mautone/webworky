import asyncio
import websockets
import logging
import json
import argparse

class WebWorky:
    def __init__(self, host="localhost", port=8765, debug=False):
        self.host = host
        self.port = port
        self.hooks = {}
        self.logger = logging.getLogger("WebWorky")
        self.logger.setLevel(logging.INFO)
        if debug:
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler("server.log")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(handler)

    def register_hook(self, message_name, hook_function):
        self.hooks[message_name] = hook_function

    async def handle_message(self, websocket, message):
        client = websocket.remote_address
        try:
            data = json.loads(message)
            message_name = data.get('message')
            payload = data.get('payload')

            if message_name in self.hooks:
                try:
                    response = await self.hooks[message_name](websocket, payload)
                    if response:
                        await websocket.send(json.dumps(response))
                        self.logger.info(f"Sent response to {client}: {json.dumps(response)}")
                except Exception as e:
                    self.logger.error(f"Error in hook for message: {message_name} from {client}: {e}")
            else:
                self.logger.warning(f"No hook registered for message: {message_name} from {client}")

            self.logger.info(f"Received message from {client}: {message}")
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON received from {client}: {message}")
        except Exception as e:
            self.logger.error(f"Unexpected error handling message from {client}: {e}")

    async def server_handler(self, websocket, path):
        client = websocket.remote_address
        self.logger.info(f"Client connected: {client}")
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.info(f"Client disconnected: {client}")
        except Exception as e:
            self.logger.error(f"Unexpected error with client {client}: {e}")

    async def start_server(self):
        try:
            self.logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            server = await websockets.serve(self.server_handler, self.host, self.port)
            await server.wait_closed()
        except Exception as e:
            self.logger.error(f"Server error: {e}")

# # Esempio di utilizzo della classe WebWorky
# async def example_hook(websocket, payload):
#     response = {"message": "response_example", "payload": {"status": "received", "data": payload}}
#     return response

# def main():
#     parser = argparse.ArgumentParser(description="Webworky websocket Server")
#     parser.add_argument('--debug', action='store_true', help='Enable debug logging to console')
#     args = parser.parse_args()

#     webworky = WebWorky(debug=args.debug)
#     webworky.register_hook("example_message", example_hook)
    
#     # Avvio dell'event loop
#     asyncio.run(webworky.start_server())

# if __name__ == "__main__":
#     main()
