# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

from base64 import b64decode, b64encode
from constants import *
from errno import ENAMETOOLONG
from traceback import print_tb
import os
import socket
import sys


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.socket = socket
        self.directory = directory
        self.buffer = ''
        self.connected = True

    def get_file_listing(self):
        dirs = os.listdir(self.directory)
        message = '0 OK' + EOL
        self.socket.send(message.encode("ascii"))
        for file in dirs:
            message = file + EOL
            self.socket.send(message.encode("ascii"))
        self.socket.send(EOL.encode("ascii"))

    def get_metadata(self, filename):
        path = self.directory + "/" + filename
        try:
            size = os.path.getsize(path)
            message = '0 OK' + EOL
            self.socket.send(message.encode("ascii"))
            message = str(size) + EOL
            self.socket.send(message.encode("ascii"))
        except OSError:
            message = "202 FILE_NOT_FOUND" + EOL
            self.socket.send(message.encode("ascii"))

    def get_slice(self, filename, offset, size):
        path = self.directory + "/" + filename
        try:
            file = open(path, "rb")  # abrimos archivo
            offset = int(offset)
            size = int(size)
            size_file = os.path.getsize(path)
            if (size_file < offset + size) or (offset < 0) or (size < 0):
                message = "203 BAD_OFFSET" + EOL
                self.socket.send(message.encode("ascii"))
            else:
                file.seek(offset)  # nos paramos en offset
                data = file.read(size)  # guardamos size bytes en data
                result = b64encode(data).decode() + EOL  # codificamos
                file.close()
                message = '0 OK' + EOL
                self.socket.send(message.encode("ascii"))
                self.socket.send(result.encode("ascii"))

        except FileNotFoundError:
            message = "202 FILE_NOT_FOUND" + EOL
            self.socket.send(message.encode("ascii"))
        except ValueError:
            message = "201 INVALID_ARGUMENTS" + EOL
            self.socket.send(message.encode("ascii"))

    def quit(self):
        print("\nConnection Closed")
        message = '0 OK' + EOL
        self.socket.send(message.encode("ascii"))
        self.connected = False
        return self.socket.close()

    def parser(self):
        while EOL not in self.buffer and self.connected:
            recv = self.socket.recv(4096)
            print("\nRecv = %s" % (recv))
            self.buffer += recv.decode("ascii")
            print("\nBuffer = %s" % (self.buffer))

        if EOL in self.buffer:
            pos1 = self.buffer.find("\r")
            pos2 = self.buffer.find("\n")
            exists = (pos1 > -1) and (pos2 > -1)
            equal = pos1 + 1 == pos2
            if (not ((equal) and (exists))):
                message = "100 BAD_EOL" + EOL
                self.socket.send(message.encode("ascii"))

            response, self.buffer = self.buffer.split(EOL, 1)
            return response.split()  # devolvemos array del primer comando encontrado
        else:
            return ""

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        print("\nNew Connection")
        try:
            while self.connected:
                message = self.parser()
                inv_arg = "201 INVALID_ARGUMENTS" + EOL
                inv_cmm = "200 INVALID_COMMAND" + EOL

                if (message[0] == "get_file_listing"):
                    if len(message) == 1:
                        self.get_file_listing()
                    else:
                        self.socket.send(inv_arg.encode("ascii"))

                elif (message[0] == "get_metadata"):
                    if len(message) == 2:
                        self.get_metadata(message[1])
                    else:
                        self.socket.send(inv_arg.encode("ascii"))

                elif (message[0] == "get_slice"):
                    if len(message) == 4:
                        self.get_slice(message[1], message[2], message[3])
                    else:
                        self.socket.send(inv_arg.encode("ascii"))

                elif (message[0] == "quit"):
                    if len(message) == 1:
                        self.quit()
                    else:
                        self.socket.send(inv_arg.encode("ascii"))
                else:
                    self.socket.send(inv_cmm.encode("ascii"))
        except Exception:
            bad_req = "101 BAD_REQUEST" + EOL
            self.socket.send(bad_req.encode("ascii"))
            print("\nConnection Closed")
            self.socket.close()
