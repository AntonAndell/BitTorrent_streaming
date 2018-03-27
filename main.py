import sys, bencoder, requests, hashlib, random
from string import ascii_letters, digits
import ipaddress, struct
VERSION = '0001'
ALPHANUM = ascii_letters + digits
DEFAULT_PORT = "55308"
class Torrent(object):
    def __init__(self, torrent_path, port=DEFAULT_PORT):
        self.torrent_dict = self.get_torrent_dict(torrent_path)
        self.peer_addresses = []
        self.port = port


    @property
    def torrent_payload(self):
        payload = {}
        info_hash = hashlib.sha1(bencoder.encode(self.torrent_dict[b'info'])).digest()
        peer_id = ('-DR' + VERSION + ''.join(random.sample(ALPHANUM, 13)))
        payload['info_hash'] = info_hash
        payload['peer_id'] = peer_id
        payload['port'] = self.port
        payload['uploaded'] = '0'
        payload['downloaded'] = '0'
        payload['left'] = str(self.torrent_dict[b'info'][b'length'])
        payload['compact'] = '1'
        payload['supportcrypto'] = '1'
        payload['event'] = 'started'
        return payload

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

t = Torrent("/home/andell/BitTorrrent_streaming/archlinux-2018.03.01-x86_64.iso.torrent")
t.get_peer_addresses()
print(t.peer_addresses)
