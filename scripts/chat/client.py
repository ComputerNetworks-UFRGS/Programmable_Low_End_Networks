import asyncio
import websockets
import sys

async def chat():
    uri = "ws://143.54.49.34:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to chat server.")
        
        async def send():
            while True:
                msg = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
                await websocket.send(msg)

        async def receive():
            while True:
                msg = await websocket.recv()
                # Print message, and re-display prompt nicely
                sys.stdout.write(f"\r< {msg}\n> ")
                sys.stdout.flush()

        await asyncio.gather(send(), receive())

if __name__ == "__main__":
    asyncio.run(chat())
