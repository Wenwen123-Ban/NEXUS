from __future__ import annotations

import socket
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.link.listener import start_listener, stop_listener
from modules.link.sender import send_message


class LinkTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reservation:
            reservation.bind(("127.0.0.1", 0))
            self.port = reservation.getsockname()[1]

        self.ready = threading.Event()
        self.errors: list[OSError] = []

        def on_ready(error: OSError | None) -> None:
            if error:
                self.errors.append(error)
            self.ready.set()

        self.listener = threading.Thread(
            target=start_listener,
            kwargs={"port": self.port, "username": "Receiver", "on_ready": on_ready},
            daemon=True,
        )
        self.listener.start()
        self.assertTrue(self.ready.wait(2), "listener did not start")
        self.assertEqual(self.errors, [])

    def tearDown(self) -> None:
        stop_listener()
        self.listener.join(2)

    def test_message_and_discovery_are_acknowledged(self) -> None:
        self.assertTrue(send_message("127.0.0.1", self.port, "Sender", "hello"))

        with socket.create_connection(("127.0.0.1", self.port), timeout=2) as peer:
            peer.sendall(b"NEXUS_DISCOVER|Sender|192.168.1.2")
            self.assertEqual(peer.recv(1024), b"NEXUS_HELLO|Receiver")


if __name__ == "__main__":
    unittest.main()
