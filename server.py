#  coding: utf-8 
import socketserver
import os
import datetime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2022 Yicheng Hu
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):
    def statu_405(self):
        send = "HTTP/1.1 405 Method Not Allowed\r\n"
        self.request.sendall(bytearray(send, "utf-8"))
    def statu_404(self):
        send = "HTTP/1.1 404 Not Found\r\n"
        self.request.sendall(bytearray(send, "utf-8"))
    def statu_200(self,content_type, content_len, file):
        date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")
        send = f"HTTP/1.1 200 OK\r\nDate: {date}\r\nContent-Length: {content_len}\r\nContent-Type: {content_type}\r\nConnection: Closed\r\n\r\n{file}"
        self.request.sendall(bytearray(send, "utf-8"))
    def statu_301(self, path):
        send = f"HTTP/1.1 301 Moved Permanently\n Location:http://HTTP/1.1{path}/\r\n\r\n "
        self.request.sendall(bytearray(send, "utf-8"))
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        data_decode = self.data.decode("utf-8")
        header_string = data_decode.split("\r\n")[0]

        try:
            header = header_string.split(" ")
        except:
            self.statu_404()

        if header[0] != "GET":
            self.statu_405()
        
        self.handle_request(header[1])

        self.request.sendall(bytearray("OK",'utf-8'))
    
    def handle_request(self, relative_path):
        if relative_path.endswith("/"):
            relative_path += "index.html"
        
        path = os.path.join("www", relative_path[1:])
        if not os.path.exists(path):
            self.statu_404()
            return

        if os.path.isfile(path):
            if not path.endswith(".html") and not path.endswith(".css"):
                self.statu_404()
                return
            self.send_file(path)
            return

        if os.path.isdir(path):
            self.handle_directory(path)
            return

    def send_file(self, path):
        f = open(path, "r")
        return_text = f.read()
        
        content_length = len(return_text)
        if path.endswith(".css"):
            content_type = "text/css"
        else:
            content_type = "text/html"
        self.statu_200(content_type, content_length, return_text)


    def handle_directory(self, path):
        if not path.endswith("/"):
            path += "/"
            self.statu_301(path)
            
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()