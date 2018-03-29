import sys, bencoder, requests, hashlib, random
from string import ascii_letters, digits
import ipaddress, struct
import socket
VERSION = '0001'
ALPHANUM = ascii_letters + digits
DEFAULT_PORT = "55308"

CLIENT_NAME = "pytorrent"
CLIENT_ID = "PY"
CLIENT_VERSION = "0001"
def generate_peer_id():
	""" Returns a 20-byte peer id. """

	# As Azureus style seems most popular, we'll be using that.
	# Generate a 12 character long string of random numbers.
	random_string = ""
	while len(random_string) != 12:
		random_string = random_string + random.choice("1234567890")

	return "-" + CLIENT_ID + CLIENT_VERSION + "-" + random_string

class Torrent(object):
    def __init__(self, torrent_path, port=DEFAULT_PORT):
        self.torrent_dict = self.get_torrent_dict(torrent_path)
        self.peer_addresses = []
        self.port = port
        self.peer_id = generate_peer_id()
    @property
    def torrent_payload(self):
        payload = {}

        payload['info_hash']  = self.info_hash
        payload['peer_id']    = self.peer_id
        payload['port']       = self.port
        payload['uploaded']   = '0'
        payload['downloaded'] = '0'
        payload['left']       = str(self.torrent_dict[b'info'][b'length'])
        payload['compact']    = '1'
        payload['event']      = 'started'
        return payload

    @property
    def info_hash(self):
        info_hash = hashlib.sha1(bencoder.encode(self.torrent_dict[b'info']))
        return info_hash.digest()
    def get_peer_addresses(self):
        tracker_adress = self.torrent_dict[b'announce']
        r = requests.get(tracker_adress, params=self.torrent_payload)
        peers_data = bencoder.decode(r.content)[b'peers']
        for i in range(0,len(peers_data), 6):
            addres_bytes = peers_data[i:i+4]
            port_bytes = peers_data[i+4:i+6]
            ip_addr = str(ipaddress.IPv4Address(addres_bytes))
            port = struct.unpack('>H', port_bytes)
            self.peer_addresses.append((ip_addr, *port))

    def get_torrent_dict(self, torrent_path):
        with open(torrent_path, "rb") as fs:
            torrent = bencoder.decode(fs.read())
        return torrent

class Peer(object):
    def __init__(self, ip, port, torrent):
        self.choked = True
        self.interested = False
        self.ip = ip
        self.port = port
        self.torrent = torrent
        self.s = None
    @property
    def address(self):
        return (self.ip, (self.port))
    def get_packet(self):
        handshake = bytes(chr(19), "utf-8") + b"BitTorrent protocol" + bytes(8*chr(0), "utf-8") + self.torrent.info_hash + bytes(self.torrent.peer_id, "utf-8")
        return handshake
    def handshake(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(True)
        self.s.settimeout(0.5)
        self.s.connect(self.address)
        print("connected")
        self.s.send(self.get_packet())
        data = self.s.recv(68)
        if not data:
            print("nope")
        print('From {} received: {}'.format(self.s.fileno(), repr(data)))
t = Torrent("/home/andell/BitTorrrent_streaming/archlinux-2018.03.01-x86_64.iso.torrent")
t.get_peer_addresses()
print("begin")
for x in range(len(t.peer_addresses)):

    try:
        p = Peer(t.peer_addresses[x][0],t.peer_addresses[x][1], t)
        p.handshake()
        pass
    except:
        print("prob timeout1")
        pass
