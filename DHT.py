import libtorrent as lt
from sys import argv
import time

atp = {}
magnet_link = "magnet:?xt=urn:btih:c1e797e823900db479b3ec2fb3bd18fe44c89f30&dn=archlinux-2018.05.01-x86_64.iso&tr=udp://tracker.archlinux.org:6969&tr=http://tracker.archlinux.org:6969/announce"
session = lt.session()
atp = lt.parse_magnet_uri(magnet_link)
session.start_dht()
session.add_dht_node(("dht.libtorrent.org", 25401))


atp["save_path"] = "/home/a/DHTproject/"
atp["storage_mode"] = lt.storage_mode_t.storage_mode_sparse
atp["paused"] = False
atp["auto_managed"] = True

user = session.add_torrent(atp)

while True:
    status = user.status()
    print(status.num_peers)
    print(status.download_rate)
    print("--------------------)
    print(status.num_pieces)
    print("--------------------")
    for peer in status.handle.get_peer_info():
        print(peer.ip)
    time.sleep(2)
