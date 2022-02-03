import os
import mimetypes
import time
from config import *
from headers import *


class Get:
    def status_line(self, status_code):
        try:
            status = status_codes[status_code]
            line = "HTTP/1.1 %s %s\r\n" % (status_code, status)
            return line.encode()
        except Exception as e:
            print('Error in get status line',e)


    def GET(self, request, address, method = 'GET'):
        try:
            path = request.uri
            parsed_headers, request_body = request.parser()
            
            if (path == '/' or path == '/index.html'):
                path = "index.html"
            else:
                real_path = [x for x in path.split('%20')]
                path = ''
                for i in real_path:
                    path += i + ' '
                path = path[:-1]
                path = DOCUMENT_ROOT + path
            gen_head = General_Headers(parsed_headers,path)
            req_head = Request_Headers(parsed_headers,path)
            ent_head = Entity_Headers(parsed_headers,path)
            resp_head = Response_Headers(parsed_headers,path)

            if os.path.exists(path) and os.path.isfile(path): 
                if(os.access(path,os.R_OK)):
                    status_line = self.status_line(200)    
                    if(os.access(path,os.W_OK)):
                        ent_head.allow = "GET, HEAD, POST, PUT, DELETE"
                    else:
                        ent_head.allow = "GET, HEAD"
                    content_type = mimetypes.guess_type(path)[0] or "text/html"
                    ent_head.content_type = content_type
                    with open(path, 'rb') as f:
                        response_body = f.read()
                    response_length = len(response_body)
                else:
                    status_line = self.status_line(403)
                    response_body = generate_error_response(403)
                    
            else:
                status_line = self.status_line(404)
                response_body = generate_error_response(404)
                ent_head.allow = None
                blank_line = b'\r\n'
                response_headers = gen_head.generate_general_header() + ent_head.generate_entity_headers() + resp_head.generate_response_header()
                response_headers = response_headers.encode()
                response = b''.join([status_line, response_headers, blank_line, response_body])
                return response, 1, False
            error_flag = False

            if('Accept' in parsed_headers.keys() and not error_flag):
                accept_status = req_head.handle_accept()
                if(accept_status != 200):
                    status_line = self.status_line(accept_status)
                    response_body = generate_error_response(accept_status)
                    ent_head.content_type = "text/html"
                    error_flag = True
            if('If-Modified-Since' in parsed_headers.keys() and not error_flag):
                if_modified_status = req_head.handle_if_modified_since(path)
                ent_head.handle_last_modified(path)
                if(if_modified_status != 200):
                    status_line = self.status_line(if_modified_status)
                    response_body = generate_error_response(if_modified_status)
                    ent_head.content_type = "text/html"
                    error_flag = True
            if('If-Unmodified-Since' in parsed_headers.keys() and not error_flag):
                if_unmodified_status = req_head.handle_if_unmodified_since(path)
                ent_head.handle_last_modified(path)
                if(if_unmodified_status != 200):
                    status_line = self.status_line(if_unmodified_status)
                    response_body = generate_error_response(if_unmodified_status)
                    ent_head.content_type = "text/html"
                    error_flag = True
            if(req_head.handle_host() == 400):
                status_line = self.status_line(400)
                response_body = generate_error_response(400)
                ent_head.content_type = "text/html"
                error_flag = True
            if('If-Match' in parsed_headers.keys() and not error_flag):
                if_match_status = req_head.handle_if_match(path, len(response_body))
                if(if_match_status != 200):
                    status_line = self.status_line(if_match_status)
                    response_body = generate_error_response(if_match_status)
                    ent_head.content_type = "text/html"
                    error_flag = True
            if('Range' in parsed_headers.keys() and not error_flag):
                range_status, ranges, response_body, full_length = req_head.handle_range(response_body)
                if(range_status == 416):
                    status_line = self.status_line(416)
                    response_body = generate_error_response(416)
                    ent_head.content_type = "text/html"
                    error_flag = True
                else:
                    ent_head.content_range = ''
                    for i in ranges:
                        start_end = i.split('-')
                        if(start_end[1] == ''):
                            ent_head.content_range += i + str(full_length - 1) + '/' + str(full_length) + ' '
                        elif(start_end[0] == ''):
                            ent_head.content_range += str(full_length - int(start_end[1])) + '-' + str(full_length - 1) + '/' + str(full_length) + ' '
                        else:
                            start = int(start_end[0])
                            end = int(start_end[1])
                            if(end > full_length):
                                i = str(start) + '-' + str(full_length - 1)
                            ent_head.content_range += i + '/' + str(full_length) + ' '
            if('Accept-Encoding' in parsed_headers.keys() and not error_flag):
                accept_enco, response_body = req_head.handle_accept_encoding(response_body)
                ent_head.content_encoding = accept_enco
            
            if(status_line.decode()[9:12] == '200' and method == 'GET'):
                exp_time = time.time()
                exp_time += 24 * 3600
                ent_head.expires = "" + time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime(exp_time))
                resp_head.generate_etag(path)
                resp_head.handle_set_cookie(address);
            response_length = len(response_body)
            ent_head.content_length = response_length
            if(error_flag):
                ent_head.allow = None
                ent_head.content_encoding = None
                ent_head.last_modified = None
            blank_line = b'\r\n'
            response_headers = gen_head.generate_general_header() + ent_head.generate_entity_headers() + resp_head.generate_response_header()
            response_headers = response_headers.encode()
            pnp = gen_head.handle_connection()
            gen_head.handle_keep_alive()
            
            if(method == 'HEAD'):
                response = b''.join([status_line, response_headers, blank_line, b''])
                return response, pnp, False
            response = b''.join([status_line, response_headers, blank_line, response_body])
            return response, pnp, False
        except Exception as e:
            print('Error in GET', e)
            return 'error in get'.encode(), 0, True
