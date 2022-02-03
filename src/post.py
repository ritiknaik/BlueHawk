import sys
from headers import *
import os
from config import *


class Post:
    def status_line(self, status_code):
        status = status_codes[status_code]
        line = "HTTP/1.1 %s %s\r\n" % (status_code, status)
        return line.encode()

    
    def POST(self, request):
        try:
            path = request.uri
            parsed_headers, request_body = request.parser()
            
            if path == '/':
                path = "index.html"
            else:
                real_path = [x for x in path.split('%20')]
                path = ''
                for i in real_path:
                    path += i + ' '
                path = path[:-1]
                path = DOCUMENT_ROOT + path

            content_ext = list(content_table.keys())
            content_typ = list(content_table.values())

            error_flag = False
            gen_head = General_Headers(parsed_headers,path)
            req_head = Request_Headers(parsed_headers,path)
            ent_head = Entity_Headers(parsed_headers,path)
            resp_head = Response_Headers(parsed_headers,path)
            sp = path.rsplit('.',1)
            ext = sp[-1]
            typ = ent_head.content_type
            # if('Content-Encoding' in parsed_headers.keys() and not error_flag):
            #     content_code ,request_body = ent_head.handle_content_encoding(request_body)

            #     if(content_code != 200):
            #         status_line = self.status_line(content_code)
            #         response_body = generate_error_response(content_code)
            #         error_flag = True
            if (os.path.exists(path) and os.path.isfile(path) and not error_flag): 
                if(os.access(path,os.W_OK)):
                    status_line = self.status_line(200)    
                    ent_head.content_type = "text/html"

                    if(ext == 'txt' or ext == 'html' or ext == 'xml' or ext == 'csv'):
                        with open('../files/post.txt', 'ab') as f:
                            f.write(request_body.encode('ISO-8859-1'))
                    else:
                        with open(path, 'wb') as f:
                            f.write(request_body.encode('ISO-8859-1'))
                    response_body = '<h1>POST Success</h1>'.encode()
                else:
                    status_line = self.status_line(405)
                    response_body = generate_error_response(405)
                    ent_head.allow = 'GET, HEAD'
                    error_flag = True
            elif os.path.exists(path) and os.path.isdir(path) and not error_flag:
                try:
                    loc = path + '/index.' + content_ext[content_typ.index(typ)]
                    f = open(loc, 'wb')
                    f.write(request_body.encode('ISO-8859-1'))
                    f.close()
                    ent_head.allow = 'GET, HEAD, POST, PUT, DELETE'
                    ent_head.content_location = loc
                    status_line = self.status_line(201)
                    response_body = '<h1>201 Created</h1>'.encode()
                except Exception as e:
                    print("Error in creating post", e)
                    sys.exit(1)
            else:
                status_line = self.status_line(201)
                response_body = '<h1>201 Created</h1>'.encode()
                if(len(sp) > 1):
                    try: 
                        f = open(path,'wb')
                        if('Content-Encoding' in parsed_headers.keys() and not error_flag):
                            content_code ,request_body = ent_head.handle_content_encoding(request_body)
                            if(content_code != 200):
                                status_line = self.status_line(content_code)
                                response_body = generate_error_response(content_code)
                                error_flag = True
                        if(not error_flag):
                            f.write(request_body.encode('ISO-8859-1'))
                            ent_head.allow = 'GET, HEAD, POST, PUT, DELETE'
                        f.close()
                    except FileNotFoundError:
                        directry, file_name = path.rsplit('/',1)
                        try:
                            os.makedirs(directry)
                            f = open(path, 'wb')
                            f.write(request_body.encode('ISO-8859-1'))
                            f.close()
                            ent_head.allow = 'GET, HEAD, POST, PUT, DELETE'
                        except OSError:
                            print("OSError")
                            # sys.exit(1)
                else:
                    directry = path
                    try:
                        os.makedirs(directry)
                        loc = path + '/index.' + content_ext[content_typ.index(typ)]
                        f = open(loc, 'wb')
                        f.write(request_body.encode('ISO-8859-1'))
                        f.close()
                        ent_head.content_location = loc
                        ent_head.allow = 'GET, HEAD, POST, PUT, DELETE'
                    except OSError:
                        print("OSError")
                        # sys.exit(1)

            if(req_head.handle_host() == 400 and not error_flag):
                    status_line = self.status_line(400)
                    response_body = generate_error_response(400)
                    ent_head.content_type = "text/html"
                    error_flag = True
            response_length = len(response_body)
            ent_head.content_length = response_length
            blank_line = b'\r\n'
            response_headers = gen_head.generate_general_header() + ent_head.generate_entity_headers() + resp_head.generate_response_header()
            response_headers = response_headers.encode()
            pnp = gen_head.handle_connection()
            gen_head.handle_keep_alive()
            response = b''.join([status_line, response_headers, blank_line, response_body])
            return response, pnp, False
        except Exception as e:
            print('Error in POST', e)
            return 'post'.encode(), 0, True