
import socket
import json
from concurrent.futures import ThreadPoolExecutor

from protocol import send_message, receive_message
from storage import Storage


HOST = "0.0.0.0"
PORT = 9090
MAX_WORKERS = 10

storage = Storage()


def process_request(request):
    if not isinstance(request, dict):
        return {"status": "error", "message": "Invalid request"}

    action = request.get("action")

    if action == "PUT":
        if "key" not in request or "value" not in request:
            return {"status": "error", "message": "Missing key or value"}

        storage.put(request["key"], request["value"])
        return {"status": "ok"}

    elif action == "GET":
        if "key" not in request:
            return {"status": "error", "message": "Missing key"}

        value = storage.get(request["key"])
        return {"status": "ok", "value": value}

    elif action == "ENQUEUE":
        if "task" not in request:
            return {"status": "error", "message": "Missing task"}

        storage.enqueue(request["task"])
        return {"status": "ok"}

    elif action == "DEQUEUE":
        timeout = request.get("timeout", 1)

        if not isinstance(timeout, (int, float)) or not 0 <= timeout <= 30:
            return {"status": "error", "message": "Invalid timeout"}

        task = storage.dequeue(timeout=timeout)
        return {"status": "ok", "task": task}

    return {"status": "error", "message": "Unknown action"}


def handle_client(client_socket, address):
    try:
        with client_socket:
            while True:
                try:
                    request = receive_message(client_socket)
                except ConnectionError:
                    break
                except (ValueError, UnicodeError, json.JSONDecodeError) as error:
                    send_message(
                        client_socket,
                        {"status": "error", "message": str(error)}
                    )
                    break

                response = process_request(request)
                send_message(client_socket, response)

    except (ConnectionError, OSError) as error:
        print(f"[!] Client {address} disconnected: {error}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()

        print(f"[*] Server initialized on {HOST}:{PORT}", flush=True)
        print(
            f"[*] Thread Pool initialized with max_workers={MAX_WORKERS}...",
            flush=True
        )

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            while True:
                client_socket, address = server.accept()
                executor.submit(handle_client, client_socket, address)


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
