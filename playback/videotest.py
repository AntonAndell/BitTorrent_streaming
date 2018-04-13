import subprocess, socket

PORT = 5554
ADDRESS = "127.0.0.1"
subprocess.Popen(["ffplay", "tcp://{}:{}?listen".format(ADDRESS, PORT)])

#Simulate chunks
def split_into_chunks(data, nr_chunks):
    chunk_size = int(len(data) / nr_chunks)
    chunks = []
    for i in range(nr_chunks):
        chunks.append(data[i*chunk_size: (i+1)*chunk_size])
        
    return chunks

with open("../sample.mkv", "rb") as f:
    nr_chunks = 100
    file = f.read()
    chunks = split_into_chunks(file, nr_chunks)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))

    for i in range(nr_chunks):
        s.sendall(chunks[i])

