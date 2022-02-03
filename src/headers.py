import random
import time
import os
import sys
from datetime import datetime, timezone
import gzip, zlib
import pandas as pd
from config import *
import socket
from threading import Thread

# def aprint(type,string):
#     if(type == 1 or type == 2):
#         print(string)
#     else:
#         pass
    

status_codes = {
        200:"OK",
        201:"Created",
        204:"No Content",
        206:"Partial Content",
        304:"Not Modified",
        400:"Bad Request",
        401:"Unauthorized",
        403:"Forbidden",
        404:"Not Found",
        405:"Method Not Allowed",
        406:"Not Acceptable",
        412:"Precondition Failed",
        415:"Unsupported Media Type",
        416:"Requested Range Not Satisfiable",
        500:"Internal Server Error",
        501:"Not Implemented",
        505:"HTTP Version Not Supported",
    }

content_table = {
        "*/*": "",
        "txt": "text/plain",
        "html": "text/html",
        "php": "text/html",
        "pdf": "application/pdf",
        "csv": "text/csv",
        "css": "text/css",
        "apng": "image/apng",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "png": "image/png",
        "ico": "image/x-icon",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "json": "application/json",
        "js": "application/javascript",
        "bin": "application/octet-stream",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "webm": "video/webm",
        "mpeg": "video/mpeg",
    }

#generates error response line
def generate_error_response(status_code):
    try:
        response_body = '<h1>%s %s</h1>'%(status_code, status_codes[status_code])
        return response_body.encode()
    except Exception as e:
        print('Error in genereating error response',e)

class General_Headers:
    def __init__(self,parsed_headers,path):
        self.path = path
        self.connection = parsed_headers['Connection'] if('Connection' in parsed_headers) else None
        self.date = "" + time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
        self.server = 'BlueHawk/1.0.1'
        self.transfer_encoding = parsed_headers['Transfer-Encoding'] if('Transfer-Encoding' in parsed_headers) else None
        self.keep_alive = parsed_headers['Keep-Alive'] if('Keep-Alive' in parsed_headers) else None
        
    def generate_general_header(self):
        general_header = "Connection: " + self.connection + '\r\n' if(self.connection) else ''
        general_header += "Date: " + self.date + '\r\n'
        general_header += "Server: " + self.server + '\r\n'
        general_header += "Transfer-Encoding: " + self.transfer_encoding + '\r\n' if(self.transfer_encoding) else ''
        general_header += "Keep-Alive: " + self.keep_alive + '\r\n' if(self.keep_alive) else ''
        return general_header
    
    #handles connection header in request
    def handle_connection(self):
        try:
            if(self.connection == 'keep-alive'):
                return 1
            else:
                self.connection = 'close'
                return 0
        except Exception as e:
            print('Error in handling connection',e)
    
    #handle keep alive header
    def handle_keep_alive(self):
        if(self.keep_alive):
            timeout = self.keep_alive.split(',')[0]
            value = timeout.split('=')[-1]
            KEEP_ALIVE = int(value)
        return 


class Request_Headers:
    def __init__(self,parsed_headers,path):
        self.path = path
        self.accept = parsed_headers['Accept'] if(parsed_headers['Accept']) else None
        self.accept_charset = parsed_headers['Accept-Charset'] if('Acceppt-Charset' in parsed_headers) else None
        self.accept_encoding = parsed_headers['Accept-Encoding'] if('Accept-Encoding' in parsed_headers) else None
        self.accept_language  = parsed_headers['Accept-Language'] if('Accept-Language' in parsed_headers) else None
        self.host = parsed_headers['Host'] if('Host' in parsed_headers) else None
        self.if_modified_since = parsed_headers['If-Modified-Since'] if('If-Modified-Since' in parsed_headers) else None
        self.if_range = parsed_headers['If-Range'] if('If-Range' in parsed_headers) else None
        self.if_unmodified_since = parsed_headers['If-Unmodified-Since'] if('If-Unmodified-Since' in parsed_headers) else None
        self.if_match = parsed_headers['If-Match'] if('If-Match' in parsed_headers) else None
        self.range = parsed_headers['Range'] if('Range' in parsed_headers) else None
        self.user_agent = parsed_headers['User-Agent'] if('User-Agent' in parsed_headers) else None
        
    #handles accept header
    def handle_accept(self):
        try:
            accepts = self.accept.split(',')
            accept_q = dict()
            for i in accepts:
                types = i.split(';')
                if(types[0] == '*/*'):
                    return 200
                if(len(types) > 1):
                    q_value = types[-1].split('=')
                    accept_q.update({types[0]:q_value})
                else:
                    accept_q.update({types[0]:1})
            requested_file_extension = self.path.rsplit('.',1)[-1]
            requested_type = content_table[requested_file_extension]
            if(requested_type not in accept_q):
                status_code = 406
            else:
                status_code = 200
            return status_code
        except Exception as e:
            print('Error in handling accept',e)
    
    def handle_accept_encoding(self, request_body):
        try:
            accepts = self.accept_encoding.split(', ')
            accept_q = dict()
            for i in accepts:
                types = i.split('; ')
                if(len(types) > 1):
                    q_value = types.split('=')[-1]
                    accept_q.update({types[0]:q_value})
                else:
                    accept_q.update({types[0]:1})
            accept_q = dict(sorted(accept_q.items(), key=lambda item: item[1]))
            key_list = list(accept_q.keys())
            if(key_list[0] == 'gzip'):
                type_of_enco = 'gzip'
                response_body = gzip.compress(request_body)
            elif(key_list[0] == 'compress'):
                type_of_enco = 'identity'
                response_body = request_body
            elif(key_list[0] == 'deflate'):
                type_of_enco = 'deflate'
                response_body = zlib.compress(request_body)
            else:
                type_of_enco = 'identity'
                response_body = request_body

            return type_of_enco, response_body
        except Exception as e:
            print('Error in handling accept encoding',e)
    
    def handle_if_modified_since(self, path):
        try:
            date = self.if_modified_since
            date_obj = datetime.strptime(date, "%a, %d %b %Y %I:%M:%S %Z")
            date_msec = date_obj.timestamp()
            time_msec = os.path.getmtime(path)
            if(time_msec < date_msec):
                status_code = 304
            else:
                status_code = 200
            return status_code
        except Exception as e:
            print('Error in handling ifmodified',e)

    def handle_host(self):
        if(self.host):
            return 200
        return 400

    def handle_if_unmodified_since(self,path):
        try:
            date = self.if_unmodified_since
            date_obj = datetime.strptime(date, "%a, %d %b %Y %I:%M:%S %Z")
            date_msec = date_obj.timestamp()
            time_msec = os.path.getmtime(path)
            if(time_msec < date_msec):
                status_code = 200
            else:
                status_code = 412
            return status_code
        except Exception as e:
            print('Error in handling if_unmodified',e)

    def handle_range(self, response_body):
        try:
            full_length = len(response_body)
            ranges = self.range.split('=')[-1]
            ranges = ranges.split(', ')
            final_body = b''
            length_of_body = len(response_body)
            for i in ranges:
                start_end = i.split('-')
                if(len(start_end) > 1 and (start_end[0] != '' and start_end[1] != '')):
                    start = int(start_end[0])
                    end = int(start_end[1])
                    if(start > length_of_body):
                        return 416, [], '', 0
                    final_body += response_body[start:end]
                else:
                    if(start_end[0] == ''):
                        final_body += response_body[length_of_body - int(start_end[1]):]
                    else:
                        if(int(start_end[0]) < length_of_body):
                            final_body += response_body[int(start_end[0]):]
                        else:
                            return 416, [], '', 0
            return 200, ranges, final_body, full_length
        except Exception as e:
            print('Error in handling range',e)
    
    def handle_if_match(self, path, length_of_response):
        try:
            etags = self.if_match.split(', ')
            actual_etag = str(os.path.getmtime(path)) + str(length_of_response)
            if actual_etag in etags:
                return 200
            return 412
        except Exception as e:
            print('Error in handling if match',e)
       

class Entity_Headers:
    def __init__(self,parsed_headers,path):
        self.path = path
        self.allow = parsed_headers['Allow'] if('Allow' in parsed_headers) else None
        self.content_encoding = parsed_headers['Content-Encoding'] if('Content-Encoding' in parsed_headers) else None
        self.content_length = parsed_headers['Content-Length'] if('Content-Length' in parsed_headers) else None
        self.content_location = parsed_headers['Content-Location'] if('Content-Location' in parsed_headers) else None
        self.content_type = parsed_headers['Content-Type'] if('Content-Type' in parsed_headers) else None
        self.content_range = parsed_headers['Content-Range'] if('Content-Range' in parsed_headers) else None
        self.expires = parsed_headers['Expires'] if('Expires' in parsed_headers) else None
        self.last_modified = parsed_headers['Last-Modified'] if('Last-Modified' in parsed_headers) else None
        
    def generate_entity_headers(self):
        entity_header = "Allow: " + self.allow + '\r\n' if(self.allow) else ''
        entity_header += "Content-Encoding: " + self.content_encoding + '\r\n' if(self.content_encoding) else ''
        entity_header += "Content-Length: " + str(self.content_length) + '\r\n' if(self.content_length) else ''
        entity_header += "Content-Location: " + self.content_location + '\r\n' if(self.content_location) else ''
        entity_header += "Content-Type: " + self.content_type + '\r\n' if(self.content_type) else ''
        entity_header += "Content-Range: " + self.content_range + '\r\n' if(self.content_range) else ''
        # entity_header += "Expires: " + self.expires + '\r\n' if(self.expires) else ''
        entity_header += "Last-Modified: " + self.last_modified + '\r\n' if(self.last_modified) else ''
        return entity_header

    def handle_last_modified(self, path):
        try:
            time_sec = os.path.getmtime(path)
            self.last_modified = datetime.fromtimestamp(time_sec, timezone.utc).strftime("%a, %d %b %Y %H:%M:%S") + " GMT"
        except Exception as e:
            print('Error in handling last_modified',e)

    def handle_content_encoding(self, body):
        try:
            cont_enco = self.content_encoding
            
            if(cont_enco == 'gzip'):
                code = 200
                final_body = gzip.decompress(body)
            elif(cont_enco == 'compress'):
                code = 200
                final_body = gzip.decompress(body)
            elif(cont_enco == 'deflate'):
                code = 200
                final_body = zlib.decompress(body)
            elif(cont_enco == 'identity'):
                code = 200
                final_body = body
            else:
                code = 415
                final_body = ''

            return code, final_body
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info() #stackoverflow
            print(exc_tb.tb_lineno)
            print('Error in handling content encoding',e)
    

class Response_Headers:
    def __init__(self,parsed_headers,path):
        self.path = path
        self.accept_ranges = 'bytes'
        self.etag = parsed_headers['ETag'] if('ETag' in parsed_headers) else None
        self.location = parsed_headers['Location'] if('Location' in parsed_headers) else None
        self.keep_alive = parsed_headers['Keep-Alive'] if('Keep-Alive' in parsed_headers) else None
        self.set_cookie = parsed_headers['Set-Cookie'] if('Set-Cookie' in parsed_headers) else None
        

    def generate_response_header(self):
        response_header = "Accept-Ranges: " + self.accept_ranges + '\r\n' if(self.accept_ranges) else ''
        response_header += "ETag: " + self.etag + '\r\n' if(self.etag) else ''
        response_header += "Location: " + self.location + '\r\n' if(self.location) else ''
        response_header += "Keep-Alive: " + self.keep_alive + '\r\n' if(self.keep_alive) else ''
        response_header += "Set-Cookie: " + self.set_cookie + '\r\n' if(self.set_cookie) else ''

        return response_header
    
    def generate_etag(self, path):
        try:
            with open(path, 'rb') as a:
                file = a.read()
            length = len(file)
            self.etag = str(os.path.getmtime(path)) + str(length)
        except Exception as e:
            print('Error in generating etag',e)

    def handle_set_cookie(self,address):
        try:
            cuki = random.randint(1000000,9999999)
            address = str(address)
            self.set_cookie = 'mycookie=' + str(cuki)
            df = pd.read_csv("../cookies/cookie.csv")
            
            if address in df['Address'].to_list():
                ind = df.index[df['Address'] == address]
                df['Times'][ind] += 1
            else:
                df2 = pd.DataFrame({"Address":[address],"Cookie":[cuki],"Times":[1]})
                df = df.append(df2)
            df.to_csv('../cookies/cookie.csv',index=False)
        except Exception as e:
            print('Error in handling set_cookie',e)
    
 
