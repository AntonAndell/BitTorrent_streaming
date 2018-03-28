import sys, bencoder, requests, hashlib, random
from string import ascii_letters, digits
import ipaddress, struct
import socket
VERSION = '0001'
ALPHANUM = ascii_letters + digits
DEFAULT_PORT = "55308"
class Torrent(object):
    def __init__(self, torrent_path, port=DEFAULT_PORT):
        self.torrent_dict = self.get_torrent_dict(torrent_path)
        self.peer_addresses = []
        self.port = port
        self.peer_id = peer_id = ('-DR' + VERSION + ''.join(random.sample(ALPHANUM, 13)))
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
        info_hash = hashlib.sha1(bencoder.encode(self.torrent_dict[b'info'])).digest()
        return info_hash
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
        params = []
        params.append(chr(len("BitTorrent protocol")))
        params.append("BitTorrent protocol")
        params.append(str(chr(0)*8))
        params.append(str(self.torrent.info_hash))
        params.append(self.torrent.peer_id)
        return ''.join(params)
    def handshake(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(True)
        self.s.connect(self.address)
        self.s.send(self.get_packet())
        data = self.s.recv(68)
        print(data)
t = Torrent("/home/andell/BitTorrrent_streaming/archlinux-2018.03.01-x86_64.iso.torrent")
t.get_peer_addresses()
print(t.peer_addresses[0][0],t.peer_addresses[0][1])
p = Peer(t.peer_addresses[0][0],t.peer_addresses[0][1], t)
p.handshake()
