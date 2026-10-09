
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from protocol import send_message, receive_message


HOST = "127.0.0.1"
PORT = 9090
NUM_WORKERS = 20


def worker(worker_id):
    with socket.create_connection((HOST, PORT), timeout=15) as sock:
        sock.settimeout(15)

        key = f"worker_{worker_id}"
        value = f"value_{worker_id}"

        send_message(sock, {
            "action": "PUT",
            "key": key,
            "value": value
        })

        response = receive_message(sock)
        assert response["status"] == "ok"

        send_message(sock, {
            "action": "GET",
            "key": key
        })

        response = receive_message(sock)
        assert response["status"] == "ok"
        assert response["value"] == value

        return worker_id


def main():
    print("Starting stress test with 20 concurrent workers...")

    completed = 0

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [
            executor.submit(worker, i)
            for i in range(NUM_WORKERS)
        ]

        for future in as_completed(futures):
            worker_id = future.result()
            completed += 1
            print(f"Worker {worker_id}: completed successfully")

    print(f"\nStress test completed: {completed}/{NUM_WORKERS} workers")
    assert completed == NUM_WORKERS


if __name__ == "__main__":
    main()
