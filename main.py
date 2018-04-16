import sys, bencoder, requests, hashlib, random
from string import ascii_letters, digits
import ipaddress, struct
import socket
import time, sys
import threading

from bitstring import BitArray
VERSION = '0001'
ALPHANUM = ascii_letters + digits
DEFAULT_PORT = "55308"

CLIENT_NAME = "mytorrent"
CLIENT_ID = "PY"
CLIENT_VERSION = "0001"
REQUEST_SIZE = 2 ** 14
def generate_peer_id():
	""" Returns a 20-byte peer id. """

	# As Azureus style seems most popular, we'll be using that.
	# Generate a 12 character long string of random numbers.
	random_string = ""
	while len(random_string) != 12:
		random_string = random_string + random.choice("1234567890")

	return "-" + CLIENT_ID + CLIENT_VERSION + "-" + random_string

class myThread (threading.Thread):
    def __init__(self, threadID, name, peer):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.peer = peer
    def run(self):
        print( "Starting " + self.name)
        while not self.peer.handshake():
            self.change_peer()
        while 1:
            self.peer.msg_loop()
            self.change_peer()


    def change_peer(self):
        self.peer = self.peer.torrent.get_random_peer()
        while not self.peer.handshake():
                self.peer = self.peer.torrent.get_random_peer()



class Torrent(object):
    def __init__(self, torrent_path, port=DEFAULT_PORT):
        self.torrent_dict = self.get_torrent_dict(torrent_path)
        self.peer_addresses = []
        self.port = port
        self.handshaked_peers = {}
        self.threads = []
        self.lock = threading.Lock()
        self.peer_id = generate_peer_id()
        self.pieces = len(self.torrent_dict[b'info'][b'pieces'])/20
        self.bitfield = ["0"]*(len(self.torrent_dict[b"info"][b"pieces"])//20)
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
    def get_random_peer(self):
        peer = random.choice(self.peer_addresses)
        if peer[0] in self.handshaked_peers:
            return self.handshaked_peers[peer[0]]
        else:
            return Peer(peer[0], peer[1], self)
    def download(self):
        for x in range(5):
            addr = random.choice(self.peer_addresses)
            peer = Peer(addr[0],addr[1], self)
            thread = myThread(x, "peer-" + str(x), peer)
            thread.start()
            self.threads.append(thread)

    def get_thread_with_slowest_peer():
        pass
    def get_peer_addresses(self):
        tracker_adress = self.torrent_dict[b'announce']
        r = requests.get(tracker_adress, params=self.torrent_payload)
        peers_data = bencoder.decode(r.content)[b'peers']
        for i in range(0,len(peers_data), 6):
            addres_bytes = peers_data[i:i+4]
            port_bytes = peers_data[i+4:i+6]
            ip_addr = str(ipaddress.IPv4Address(addres_bytes))
            port = struct.unpack('>H', port_bytes)
            self.peer_addresses.append((ip_addr, port[0]))

    def get_torrent_dict(self, torrent_path):
        with open(torrent_path, "rb") as fs:
            torrent = bencoder.decode(fs.read())
        return torrent
    """
    def get_next_piece():
        for i in range(len(bitfield)):
            if bitfield[i] == "0":
                bitfield[i] == "-"
                return i
    """



class Peer(object):
    def __init__(self, ip, port, torrent):
        self.choked = True
        self.interested = False
        self.ip = ip
        self.handshaked = False
        self.port = port
        self.torrent = torrent
        """will be a long binary string with each index of the string says if peer got that piece (1) or not (0)"""
        self.bitfield = ""
        self.s = None
        self.current_piece_index = 0

    @property
    def address(self):
        return (self.ip, (self.port))
    def msg_function(self, msg_type):
        #TODO add alot more types
        return {5:self.bitfield_msg,1:self.unchoke_msg, 4:self.have_msg, 7:self.piece_msg, 0:self.choke_msg}[msg_type]

    def get_packet(self):
        handshake = bytes(chr(19), "utf-8") + b"BitTorrent protocol" + bytes(8*chr(0), "utf-8") + self.torrent.info_hash + bytes(self.torrent.peer_id, "utf-8")
        return handshake

    def handshake(self):
        if self.handshaked:
            return True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(True)
        self.s.settimeout(0.5)
        try:
            self.s.connect(self.address)
            print("connected")
            self.s.send(self.get_packet())
            data = self.s.recv(68)
        except:
            return False

        self.current_piece = None
        #TODO get location info through external source and other properties
        if not data:
            return False
        #self.msg_loop()
        self.s.settimeout(3)
        handshake = True
        self.torrent.handshaked_peers[self.ip] = self
        return True

    def msg_loop(self):
        while True:
            try:
                data = self.s.recv(5)
                try:
                    size = int.from_bytes(data[0:4], byteorder='big')
                    if(not self.msg_function(data[4])(size)):
                        return False
                except IndexError:
                    print(data)
                    print("hahah yep")
                except KeyError:
                    print("KeyError")
            except socket.error as e:
                print(e)
                return False

                #TODO check data

    def request_piece(self):
        print("REQUESTING PICEE")
        if self.choked:
            return
        i = 0
        self.torrent.lock.acquire()
        while self.current_piece_index  < self.torrent.pieces:
            #TODO selcet by algorithms
            if self.torrent.bitfield[self.current_piece_index ] == "0" and self.bitfield[self.current_piece_index ] == "1":
                self.torrent.bitfield[self.current_piece_index] = "-"
                self.torrent.lock.release()
                self.current_piece = Piece(self.current_piece_index , self.torrent.torrent_dict[b'info'][b'piece length'],)
                self.s.send(self.current_piece.get_block_msg())
                return True
            else:
                if i > 5:
                    return False
                self.current_piece_index += 1
        print("peer empty")
        return False

    def piece_msg(self, size):
        data = self.s.recv(8)
        size -= 8
        data = b''
        while len(data) < size-1:
            packet = self.s.recv(size - len(data))
            if not packet:
                return None
            data += packet
        if (self.current_piece.add_block(data)):
            if(self.current_piece.verify_piece(self.torrent.torrent_dict[b"info"][b"pieces"][self.current_piece.index*20: self.current_piece.index*20 + 20])):
                self.torrent.bitfield[int(self.current_piece.index)] = "1"
                a = self.torrent.bitfield.count("0")
                print(a)
                if (a == 0):
                    print("we are done")
                    exit()
                return self.request_piece()
            #TODO request next piece
        else:
            self.s.send(self.current_piece.get_block_msg())
            return True
    def send_interest(self):
        msg = struct.pack('>Ib', 1, 2)
        print("sending intrest msg = {}".format(msg))
        self.s.send(msg)
        return True

    def bitfield_msg(self, size):
        data= self.s.recv(size)
        self.bitfield = str(bin(int.from_bytes(data, byteorder='big')))[2:]
        #TODO check if peer has any picecs we want:
        self.interested = True
        if self.interested:
            self.send_interest()
            return True
        return False
    def have_msg(self, size):
        self.s.recv(size)
        return True
    def unchoke_msg(self, size):
        print("unchoked")
        self.choked = False
        if self.interested:
            print("we are now unchoked requesting a piece")
            self.request_piece()
            return True
        return False
    def choke_msg(self,size):
        choked = True
        return False


class Piece(object):
    """
    index: the index of the piece
    size: size in bytes
    block_offset: the place where the next block to be requested starts
    blocksize: REQUEST SIZE 2^14 standard value
    blocks: array of which blocks we go
    last_blocksize: incase size // blocksize is not even
    """
    def __init__(self, index, size , block_offset=0):
        self.index = index
        self.size = size
        self.block_offset = block_offset

        if not (size%REQUEST_SIZE == 0):
            self.block_count = size//REQUEST_SIZE + 1
            self.last_blocksize = size%REQUEST_SIZE
        else:
            self.block_count = size//REQUEST_SIZE
            self.last_blocksize = REQUEST_SIZE
        self.blocks = b""
    #TODO make this so you can request specific blocks
    def get_block_msg(self):
        if(self.block_offset + REQUEST_SIZE > self.size):
            block_size = self.last_blocksize
        else:
            block_size = REQUEST_SIZE
        msg = struct.pack('>IbIII', 13, 6, self.index, self.block_offset, block_size)
        return msg
    def add_block(self, data):
        self.blocks += data
        if self.block_offset + REQUEST_SIZE >= self.size:
            #piece done
            return True
        else:
            self.block_offset += REQUEST_SIZE
            return False
    def verify_piece(self, hash):
        if hashlib.sha1(self.blocks).digest() != hash:
            print(hashlib.sha1(self.blocks).digest())
            print(hash)
            time.sleep(5)
        print (hashlib.sha1(self.blocks).digest() == hash)
        return True



t = Torrent("/home/andell/BitTorrrent_streaming/archlinux-2018.03.01-x86_64.iso.torrent")
t.get_peer_addresses()
t.download()
