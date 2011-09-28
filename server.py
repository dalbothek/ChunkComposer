# -*- coding: utf-8 -*-
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
from threading import Timer


class Server:
    HOST = ''
    PORT = 25565
    SEPERATOR = unichr(0xa7)
    TIME = 23000

    def __init__(self, chunk, x=8, y=64, z=8):
        self.pos = (x, y, z)
        self.chunk = chunk
        self.run = True
        self.timer = None
        self.listen()
        self.accept()

    def listen(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(0)
        print "Listening on port", self.PORT

    def send(self, data):
        self.conn.send(data)

    def send_byte(self, byte):
        self.send(chr(byte))

    def send_short(self, s):
        self.send(pack('>h', s))

    def send_int(self, i):
        self.send(pack(">i", i))

    def send_long(self, l):
        self.send(pack(">q", l))

    def send_double(self, d):
        self.send(pack(">d", d))

    def send_float(self, f):
        self.send(pack(">f", f))

    def send_string(self, string):
        self.send_short(len(string))
        for c in string:
            self.send_byte(0)
            self.send_byte(ord(c))

    def read(self, n=1):
        l = 0
        data = ''
        while l < n:
            data += self.conn.recv(n - l)
            if len(data) == l:
                break
            l = len(data)
        return data

    def read_short(self):
        return unpack(">h", self.read(2))[0]

    def read_byte(self):
        return ord(self.read(1))

    def read_string(self):
        l = self.read_short()
        s = ''
        for i in range(l):
            self.read(1)
            s += unpack('c', self.read(1))[0]
        return s

    def accept(self):
        self.conn, addr = self.socket.accept()
        print "\nConnected to", addr
        try:
            if not self.wait_handshake():
                self.close()
                self.accept()
                return
            self.handshake()
            self.wait_login()
            self.login()
            self.prechunk()
            self.map()
            self.time()
            self.position()
            self.keep_alive()
            self.wait()
        except Exception as e:
            print "Unexpected error:", e
        self.close()
        self.stop()

    def wait_handshake(self):
        id = self.read_byte()
        if id == 2:
            print "  shaking hands"
            self.read_string()
            return True
        elif id == 0xfe:
            print "  sending server status"
            self.send_byte(0xff)
            self.send_string("Chunk Composer" +
                             self.SEPERATOR + "0" +
                             self.SEPERATOR + "1")
            return False
        else:
            raise Exception("Invalid packet id")

    def handshake(self):
        self.send_byte(2)
        self.send_string("-")

    def wait_login(self):
        id = self.read_byte()
        if id != 1:
            raise Exception("Invalid packet id")

    def login(self):
        print "  logging in"
        self.send_byte(1)
        self.send_int(1)
        self.send_string("")
        self.send_long(1234)
        self.send_int(1)
        self.send_byte(0)
        self.send_byte(0)
        self.send_byte(128)
        self.send_byte(1)

    def keep_alive(self):
        if not self.run:
            return
        self.send_byte(0)
        self.send_int(123)
        self.timer = Timer(10, self.keep_alive)
        self.timer.start()

    def prechunk(self):
        print "  sending pre-chunk"
        self.send_byte(0x32)
        self.send_int(0)
        self.send_int(0)
        self.send_byte(1)

    def map(self):
        print "  sending chunk"
        self.send_byte(0x33)
        self.send_int(0)
        self.send_short(0)
        self.send_int(0)
        self.send_byte(15)
        self.send_byte(127)
        self.send_byte(15)
        self.send_int(len(self.chunk))
        self.send(self.chunk)

    def position(self):
        print "  sending spawn position"
        self.send_byte(0x0d)
        self.send_double(self.pos[0])
        self.send_double(self.pos[1])
        self.send_double(self.pos[1] + 1.6)
        self.send_double(self.pos[2])
        self.send_float(0)
        self.send_float(0)
        self.send_byte(0)

    def time(self):
        print "  sending time"
        self.send_byte(4)
        self.send_long(self.TIME)

    def wait(self):
        print "  waiting for disconnect"
        data = 'x'
        while len(data) > 0:
            data = self.read(10)
        self.run = False

    def close(self):
        try:
            self.conn.close()
        except:
            pass
        print "Connection closed"

    def stop(self):
        try:
            self.socket.close()
        except:
            pass
        if self.timer:
            self.timer.cancel()
