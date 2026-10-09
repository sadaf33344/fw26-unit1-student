
import json
import struct


def recv_exact(sock, n):
    """Receive exactly n bytes from a socket."""
    data = bytearray()

    while len(data) < n:
        chunk = sock.recv(n - len(data))

        if not chunk:
            raise ConnectionError("Connection closed before all bytes arrived")

        data.extend(chunk)

    return bytes(data)


def send_message(sock, message):
    """Send a JSON message with a 4-byte length header."""
    payload = json.dumps(message).encode("utf-8")
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def receive_message(sock):
    """Receive and decode a length-prefixed JSON message."""
    header = recv_exact(sock, 4)
    message_length = struct.unpack("!I", header)[0]

    if message_length == 0 or message_length > 1024 * 1024:
        raise ValueError("Invalid message length")

    payload = recv_exact(sock, message_length)
    return json.loads(payload.decode("utf-8"))
