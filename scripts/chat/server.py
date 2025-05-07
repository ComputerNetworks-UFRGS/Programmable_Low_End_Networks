import asyncio
import websockets

connected_clients = {}  # Maps websocket -> client name
client_id_counter = 1
lock = asyncio.Lock()

async def handler(websocket):
    global client_id_counter
    async with lock:
        client_name = f"client {client_id_counter}"
        client_id_counter += 1
        connected_clients[websocket] = client_name

    print(f"{client_name} connected.")

    # Notify others that a new client has joined
    join_msg = f"🔔 {client_name} has joined the chat"
    await asyncio.gather(*[
        client.send(join_msg)
        for client in connected_clients
        if client != websocket
    ])

    try:
        async for message in websocket:
            sender = connected_clients[websocket]
            formatted_message = f"{sender} > {message}"
            await asyncio.gather(*[
                client.send(formatted_message)
                for client in connected_clients
                if client != websocket
            ])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Notify others that this client has left
        client_name = connected_clients[websocket]
        del connected_clients[websocket]
        print(f"{client_name} disconnected.")

        leave_msg = f"👋 {client_name} has left the chat"
        await asyncio.gather(*[
            client.send(leave_msg)
            for client in connected_clients
        ])

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket chat server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
