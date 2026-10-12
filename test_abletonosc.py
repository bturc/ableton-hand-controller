from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def handler(address, *args):
    print("Received:", address, args)

dispatcher = Dispatcher()
dispatcher.set_default_handler(handler)
server = BlockingOSCUDPServer(("127.0.0.1", 11001), dispatcher)

client = SimpleUDPClient("127.0.0.1", 11000)
# client.send_message("/live/test", [])
client.send_message("/live/song/get/tempo", [])
server.handle_request()  # waits for one reply