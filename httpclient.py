#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = self.get_headers(data)
        code = int(header.split()[1])
        return code

    def get_headers(self,data):
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url_content = urlparse(url)
        port = url_content.port
        host = url_content.hostname
        path = url_content.path
        if port is None:
            if url.startswith('http'):
                port = 80
            elif url.startwith('https'):
                port = 443
        if host is None:
            raise ConnectionError("no host found")
                
        if path == "":
            path = "/"

        self.connect(host,port)
        request = "GET "+path+" HTTP/1.1\r\nHost: "+host+"\r\nAccept: */*\r\nConnection: closed\r\n\r\n"
        self.sendall(request)
        
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        print(body)
        return HTTPResponse(code, body)
        

    def POST(self, url, args=None):
        url_content = urlparse(url)
        port = url_content.port
        host = url_content.hostname
        path = url_content.path
        content_type = "application/x-www-form-urlencoded"
        if port is None:
            if url.startswith('http'):
                port = 80
            elif url.startswith('https'):
                port = 443
                
        if host is None:
            raise ConnectionError("no host found")
        
        if path == "":
            path = "/"
            
        if args != None:
            args = urlencode(args)
        else:
            args =""

        self.connect(host,port)
        request = "POST "+str(path)+" HTTP/1.1\r\nHost: "+str(host)+" \r\nContent-Type: "+str(content_type)+"\r\nAccept: */*\r\nContent-Length: "+str(len(args))+"\r\nConnection: closed\r\n\r\n"+str(args)

        self.sendall(request)
        
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)
        print(body)
        return HTTPResponse(code, body)
        

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
