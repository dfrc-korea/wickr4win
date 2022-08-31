#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : decrypt.py
# Author        : bssthu
# Project       : pysqlsimplecipher
# Creation date : 2016-06-03
# Description   :
#


import sys
from pysqlsimplecipher import decryptor

class Decrypt:
    def __init__(self, filename_in, password, filename_out):
        self.filename_in = filename_in
        self.password = password
        self.filename_out = filename_out

    def main(self):
        password = bytearray(self.password.encode('utf-8'))
        decryptor.decrypt_file(self.filename_in, password, self.filename_out)


if __name__ == '__main__':
    Decrypt().main()
