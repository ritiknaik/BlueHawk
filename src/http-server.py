from get import *
from head import *
from delete import *
from post import *
from put import *
from headers import *

class TCPServer:
    
    def __init__(self, host='127.0.0.1'):
        self.host = host
        self.port = PORT
        self.arr = []

    def socket_handler_nonpersistent(self,connectionsocket,address):
        if(len(self.arr) > MAX_CONNECTIONS):
            date = "" + time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
            message = 'HTTP/1.1 500 Internal Server Error\r\nDate: ' + date + '\r\nServer: BlueHawk/1.0.1\r\n\r\n<h2>Server response: Too many connections</h2>'
            print(message)
            connectionsocket.sendall(message.encode())
            flag = False
        else:
            flag = True
        connectionsocket.settimeout(KEEP_ALIVE)
        try:
            while flag:
                data = connectionsocket.recv(1048576)
                # print('received something of length: ', len(data))
                response, pnp, exception = self.handle_HTTP_Request(data.decode('ISO-8859-1'),address)
                if(exception):
                    date = "" + time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
                    response = 'HTTP/1.1 500 Internal Server Error\r\nDate: '+date+'\r\nServer: BlueHawk/1.0.1\r\n\r\n<h2>Server Error</h2>'
                    response = response.encode()
                    print('here')
                print('Sending data to:', address)
                    
                connectionsocket.sendall(response)
                print('Sent data to:',address)
                if(pnp == 0):
                    break
                else:
                    connectionsocket.settimeout(KEEP_ALIVE)               
            self.arr.remove(connectionsocket)
            print('Connection closed for:', address)
            connectionsocket.close()
        except socket.timeout:
            self.arr.remove(connectionsocket)
            connectionsocket.close()
            print('Timeout connection closed for:', address)
        except Exception as e:
            self.arr.remove(connectionsocket)
            connectionsocket.close()
            print('Exception in socket handler', e)

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #unbinds socket from assigned port on exit
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        s.bind((self.host, self.port))
        s.listen(10)

        print("Listening at port: ",self.port)
        while True:
            connectionsocket, address = s.accept()
            print("Connected by", address)
            self.arr.append(connectionsocket)
            t=Thread(target=self.socket_handler_nonpersistent, args=(connectionsocket,address,))
            t.start()
      
    def handle_HTTP_Request(self, data):
        return 'tcp', 0, False

class HTTPRequest:
    def __init__(self, data):
        self.http_version = ''
        self.method = None
        self.headers = dict()
        self.uri = None
        self.received_headers = None
        self.body = None
        blank_line_split = data.split('\r\n\r\n',1)
        head = blank_line_split[0]
        header_lines = head.split('\r\n')
        request_line = header_lines[0] 
        request_fields = request_line.split(' ')
        self.method = request_fields[0]
        
        if len(request_fields) > 1:
            self.uri = request_fields[1]

        if len(request_fields) > 2:
            self.http_version = request_fields[2]
        print('Request received', self.method)

        self.received_headers = head
        if(len(blank_line_split) > 1):
            self.body = blank_line_split[1]      

    #parsing the request and separating headers and body
    def parser(self):
        try:
            lines = self.received_headers.split('\r\n')
            lines = lines[1:]
            for line in lines:
                # print(line)
                [x, y] = [value for value in line.split(': ',1)]
                self.headers.update({x : y})
            return self.headers, self.body
        except Exception as e:
            print('Error in parser',e)
        

class HTTPServer(TCPServer, Get, Head, Delete, Post, Put):
    
    #handle 501 error
    def handle_501(self):
        date = "" + time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
        response = 'HTTP/1.1 501 Not Implemented\r\nDate: '+date+'\r\nServer: BlueHawk/1.0.1\r\n\r\n<h1>Not Implemented</h1>'
        response = response.encode()
        return response, 0, False

    #handle correct HTTP request
    def handle_HTTP_Request(self, data, address):
        try:
            request = HTTPRequest(data)
            if(request.http_version != 'HTTP/1.1'):
                date = "" + time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
                response = 'HTTP/1.1 505 HTTP Version Not Supported\r\nDate: '+date+'\r\nServer: BlueHawk/1.0.1\r\n\r\n<h2>Server Error</h2>'
                response = response.encode()
                return response, 0, False
            if(request.method == 'GET'):
                handler = self.GET
                response, pnp, exc = handler(request, address)
            elif(request.method == 'HEAD'):
                handler = self.HEAD
                response, pnp, exc = handler(request)
            elif(request.method == 'POST'):
                handler = self.POST
                response, pnp, exc = handler(request)
            elif(request.method == 'PUT'):
                handler = self.PUT
                response, pnp, exc = handler(request)
            elif(request.method == 'DELETE'):
                handler = self.DELETE
                response, pnp, exc = handler(request)
            else:
                handler = self.handle_501
                response, pnp, exc = handler()
            return response, pnp, exc
        except Exception as e:
            print('Error in HTTP request handler', e)
            return 'error in handler'.encode(), 0, True


if __name__ == '__main__':
    try:
        server = HTTPServer()
        server.start()
    except KeyboardInterrupt:
        sys.exit(1)

