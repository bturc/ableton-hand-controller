"""Low-level OSC connection to AbletonOSC (https://github.com/ideoforms/AbletonOSC)."""

import threading
from collections import defaultdict

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

DEFAULT_HOST = "127.0.0.1"
SEND_PORT = 11000     # AbletonOSC listens here
RECEIVE_PORT = 11001  # AbletonOSC replies here


class AbletonOSC:
    """Send messages to AbletonOSC and receive its replies.

    - send(address, *args): fire and forget
    - query(address, *args): send and wait for the reply on the same address
    - on(address, handler): call handler(*args) for every message on address
      (e.g. the updates sent after /live/song/start_listen/<property>)

    Use as a context manager. Only one instance can run at a time, since it
    binds the receive port.
    """

    def __init__(self, host=DEFAULT_HOST, send_port=SEND_PORT, receive_port=RECEIVE_PORT):
        self.client = SimpleUDPClient(host, send_port)
        self._handlers = defaultdict(list)
        self._lock = threading.Lock()

        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._dispatch)
        self.server = ThreadingOSCUDPServer((host, receive_port), dispatcher)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def send(self, address, *args):
        self.client.send_message(address, list(args))

    def on(self, address, handler):
        with self._lock:
            self._handlers[address].append(handler)

    def off(self, address, handler):
        with self._lock:
            self._handlers[address].remove(handler)

    def query(self, address, *args, timeout=2.0):
        """Send a message and return the args of the reply to the same address."""
        reply = []
        received = threading.Event()

        def capture(*reply_args):
            reply.extend(reply_args)
            received.set()

        self.on(address, capture)
        try:
            self.send(address, *args)
            if not received.wait(timeout):
                raise ConnectionError(
                    f"No reply from AbletonOSC to {address}. Is Live running with "
                    "AbletonOSC selected as a Control Surface?"
                )
        finally:
            self.off(address, capture)
        return tuple(reply)

    def _dispatch(self, address, *args):
        if address == "/live/error":
            print("AbletonOSC error:", *args)
        with self._lock:
            handlers = list(self._handlers.get(address, ()))
        for handler in handlers:
            handler(*args)

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
