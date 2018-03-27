import sys, bencoder, requests, hashlib, random
from string import ascii_letters, digits
import ipaddress, struct
VERSION = '0001'
ALPHANUM = ascii_letters + digits
DEFAULT_PORT = "55308"
def download(torrent_file):
    with open(torrent_file, "rb") as fs:
    #print(torrent.read())
        torrent = bencoder.decode(fs.read())
    tracker = torrent[b'announce']
    info_hash = hashlib.sha1(bencoder.encode(torrent[b'info'])).digest()
    payload = {}

    peer_id = ('-DR' + VERSION + ''.join(random.sample(ALPHANUM, 13)))
    assert len(peer_id) == 20
    payload['info_hash'] = info_hash
    payload['peer_id'] = peer_id
    payload['port'] = DEFAULT_PORT
    payload['uploaded'] = '0'
    payload['downloaded'] = '0'
    payload['left'] = str(torrent[b'info'][b'length'])
    payload['compact'] = '1'
    payload['supportcrypto'] = '1'
    payload['event'] = 'started'

    r = requests.get(tracker, params=payload)
    peers_data = bencoder.decode(r.content)[b'peers']

    peer_ips = []
    for i in range(0,len(peers_data), 6):
        addres_bytes = peers_data[i:i+4]
        port_bytes = peers_data[i+4:i+6]
        ip_addr = str(ipaddress.IPv4Address(addres_bytes))
        port = struct.unpack('>H', port_bytes)
        peer_ips.append((ip_addr, *port))
    print(peer_ips)

download("/home/andell/BitTorrrent_streaming/archlinux-2018.03.01-x86_64.iso.torrent")
