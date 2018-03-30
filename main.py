import sys, bencoder, requests, hashlib, random
from string import ascii_letters, digits
import ipaddress, struct
import socket
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

class Torrent(object):
    def __init__(self, torrent_path, port=DEFAULT_PORT):
        self.torrent_dict = self.get_torrent_dict(torrent_path)
        self.peer_addresses = []
        self.port = port
        self.peer_id = generate_peer_id()
        self.pieces = len(self.torrent_dict[b'info'][b'pieces'])/20
        self.bitfield = "0"*50000
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
        """will be a long binary string with each index of the string says if peer got that piece (1) or not (0)"""
        self.bitfield = ""
        self.s = None

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
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(True)
        self.s.settimeout(0.5)
        self.s.connect(self.address)
        print("connected")
        self.s.send(self.get_packet())
        data = self.s.recv(68)
        self.current_piece = None
        #TODO get location info through external source and other properties
        if not data:
            print("no data")
            return
        print('From {} received: {}'.format(self.s.fileno(), repr(data)))
        self.s.setblocking(True)
        self.msg_loop()

    def msg_loop(self):
        while True:
            data = self.s.recv(5)
            try:
                print (data)
                print("reviced type {}".format(data[4]))
                size = int.from_bytes(data[0:4], byteorder='big')
                self.msg_function(data[4])(size)
            except IndexError:
                pass
            except KeyError:
                print("KeyError")
            #TODO check data

    def request_piece(self):
        i = 0
        print(self.torrent.pieces)
        while i < self.torrent.pieces:
            #TODO selcet by algorithms
            print(self.bitfield[i])
            if self.torrent.bitfield[i] == "0" and self.bitfield[i] == "1":
                self.current_piece = Piece(i, self.torrent.torrent_dict[b'info'][b'piece length'], block_offset = REQUEST_SIZE)
                self.s.send(self.current_piece.get_block_msg())
                print("sending piece request msg = {}".format(self.current_piece.get_block_msg()))
                return
            else:
                i += 1

    def piece_msg(self, size):
        print(size)
        data = b''
        while len(data) < size-1:
            packet = self.s.recv(size - len(data))
            if not packet:
                return None
            data += packet
            print(len(data))
        print(data)
        print(len(data))
        exit()
        pass
    def send_interest(self):
        msg = struct.pack('>Ib', 1, 2)
        print("sending intrest msg = {}".format(msg))
        self.interested = True
        self.s.send(msg)

    def bitfield_msg(self, size):
        data= self.s.recv(size)
        self.bitfield = str(bin(int.from_bytes(data, byteorder='big')))[2:]
        #TODO check if peer has any picecs we want:
        interested = True
        if interested:
            self.send_interest()
    def have_msg(self, size):
        self.s.recv(size)
    def unchoke_msg(self, size):
        self.choked = False
        if self.interested:
            print("we are now unchoked requesting a piece")
            self.request_piece()
    def choke_msg(self,size):
        print("chooking")

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
        self.blocks = []
        if not (size%REQUEST_SIZE == 0):
            self.block_count = size//REQUEST_SIZE + 1
            self.last_blocksize = size%REQUEST_SIZE
        else:
            self.block_count = size//REQUEST_SIZE
            self.last_blocksize = REQUEST_SIZE
    #TODO make this so you can request specific blocks
    def get_block_msg(self):
        if(self.block_offset + REQUEST_SIZE > self.size):
            block_size = self.last_blocksize
        else:
            block_size = REQUEST_SIZE
        msg = struct.pack('>IbIII', 13, 6, self.index, self.block_offset, block_size)
        return msg
    def add_block(self, data):
        self.blocks[self.block_offset/REQUEST_SIZE] = data
        if self.block_offset + REQUEST_SIZE >= self.size:
            return True
        else:
            self.block_offset += REQUEST_SIZE
            return False


t = Torrent("/home/andell/BitTorrrent_streaming/archlinux-2018.03.01-x86_64.iso.torrent")
t.get_peer_addresses()
print("begin")
for x in range(len(t.peer_addresses)):
    print(t.peer_addresses[x][0],t.peer_addresses[x][1])
    print(socket.gethostname())
    p = Peer(t.peer_addresses[x][0],t.peer_addresses[x][1], t)
    p.handshake()
    break;
    try:

        pass
    except socket.timeout:
        print("prob timeout1")
        pass
