import os
import asyncio
import urllib3
import json
import logging
import socket
import yaml

CONFIG_FILE = "/home/pi/lirc2hass.yaml"
SOCKET_PATH = "/var/run/lirc/lircd"

logging.basicConfig(
  format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
  level=os.getenv("LOGGING", logging.INFO),
  datefmt="%Y-%m-%d %H:%M:%S")

def post_hass(url, token, service, data):
  try:
    headers = {"Authorization": "Bearer {}".format(token),
               "Content-Type'": "Application/Json"}
    service = service.replace(".", "/")
    url = f"{url}/{service}"
    body = json.dumps(data).encode("utf-8")
    http = urllib3.PoolManager()
    r = http.request("POST", url, body=body, headers=headers)

    if r.status in [200, 201, 204]:
      logging.debug(f"Post to hass status code: {r.status} with data {r.data}")
      return r.data

  except Exception as err:
    logging.warning(f"Post to hass failed, because {err}")

def read_config(filename):
  try:
    with open(filename, "r") as f:
      return yaml.safe_load(f)

  except Exception as err:
    logging.critical(f"Failed reading config file {filename}, because: str({err})")
    return None

class LircProtocol(asyncio.Protocol):

    def __init__(self, config, on_con_lost):
        self.config = config
        self.transport = None
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        data = data.decode()
        lirc = data.split()
        if lirc[1] == "00":
            key = lirc[2]
            logging.info(f"{key} pressed")
            if key in self.config:
                actions = self.config[key]
                for action in actions:
                  post_hass(self.config["url"], self.config["token"], action["service"], action["data"])
            else:
              logging.info(f"{lircc[2]} is not configured")

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)

async def main():
    config = read_config(CONFIG_FILE)
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)

    transport, protocol = await loop.create_connection(
        lambda: LircProtocol(config, on_con_lost), sock=sock)

    try:
        await protocol.on_con_lost
    finally:
        transport.close()
        sock.close()

asyncio.run(main())
