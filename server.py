import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 5555))


s.settimeout(30)
d = s.recv(16)

print(d)