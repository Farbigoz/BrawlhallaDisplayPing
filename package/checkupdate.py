import socket
import json
import json.decoder
import ssl


TAG_NAME = "1.1release"

PATH = "/repos/Farbigoz/BrawlhallaDisplayPing/releases/latest"
HOST = 'api.github.com'
PORT = 443

HEADER = f"""
GET {PATH} HTTP/1.1
Host: {HOST}
User-Agent: insomnia/7.0.3
Accept: */*
""".strip().replace("\n", "\r\n")
HEADER += "\r\n\r\n"


def CheckUpdate():
    context = ssl.create_default_context()

    data = b""
    json_payload = {}

    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            ssock.send(HEADER.encode("UTF-8"))
            while True:
                _data = ssock.recv(2048)
                if ( len(_data) < 1) :
                    break
                data += _data

                data_split = data.decode().split("\r\n\r\n")
                if len(data_split) == 2:
                    payload = data_split[1]

                    try:
                        json_payload = json.loads(payload)
                        ssock.close()
                        sock.close()
                        break
                    except json.decoder.JSONDecodeError:
                        pass

    if json_payload:
        tag_name = json_payload.get("tag_name", None)
        if tag_name is not None and tag_name != TAG_NAME:
            if json_payload.get("prerelease", None) == False:
                return json_payload.get("html_url", None)

    return None
            
