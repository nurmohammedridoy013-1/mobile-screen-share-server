import asyncio
import websockets
import json
import os

clients = {}

async def handler(websocket, *args):
    client_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            print(f"Received message: {msg_type} from {data.get('id', 'unknown')}")

            if msg_type == "join":
                client_id = data.get("id")
                if client_id:
                    clients[client_id] = websocket
                    print(f"Client joined: {client_id}")
            
            else:
                target_id = data.get("target")
                if target_id and target_id in clients:
                    print(f"Forwarding {msg_type} to {target_id}")
                    await clients[target_id].send(message)
                else:
                    print(f"Target {target_id} not found for {msg_type}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed: {client_id}")
    except Exception as e:
        print(f"Error in handler: {e}")
    finally:
        if client_id and client_id in clients:
            del clients[client_id]
            print(f"Client disconnected: {client_id}")

async def main():
    port = int(os.environ.get("PORT", 8765))
    print(f"Signaling server starting on ws://0.0.0.0:{port}")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
