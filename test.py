#!/usr/bin/env python


f = open("/home/andell/BitTorrrent_streaming/SampleVideo_1280x720_5mb.mkv", "rb")
d = {}
for i in range(0,len(link), 2):
    d[link[i]] = link[i+1]

print(bencoder.decode(d["btih"]))
