
import threading
from collections import deque


class Storage:
    def __init__(self):
        self.data = {}
        self.queue = deque()

        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def put(self, key, value):
        """Store a value using its key."""
        with self.lock:
            self.data[key] = value

    def get(self, key):
        """Retrieve a value by key."""
        with self.lock:
            return self.data.get(key)

    def enqueue(self, task):
        """Add a task to the queue."""
        with self.condition:
            self.queue.append(task)
            self.condition.notify()

    def dequeue(self, timeout=None):
        """Remove the oldest task, waiting if necessary."""
        with self.condition:
            ready = self.condition.wait_for(
                lambda: len(self.queue) > 0,
                timeout=timeout
            )

            if not ready:
                return None

            return self.queue.popleft()
