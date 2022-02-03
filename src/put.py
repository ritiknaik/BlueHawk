from headers import *
import os
from config import *


class Put:
    def status_line(self, status_code):
        status = status_codes[status_code]
        line = "HTTP/1.1 %s %s\r\n" % (status_code, status)
        return line.encode()

    def PUT(self, request):
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
            error_flag = False
            
            gen_head = General_Headers(parsed_headers,path)
            req_head = Request_Headers(parsed_headers,path)
            ent_head = Entity_Headers(parsed_headers,path)
            resp_head = Response_Headers(parsed_headers,path)
            if os.path.exists(path) and os.path.isfile(path): 
                if(os.access(path,os.W_OK)):
                    status_line = self.status_line(200)    
                    ent_head.content_type = "text/html"
                    with open(path, 'wb') as f:
                        f.write(request_body.encode('ISO-8859-1'))
                    response_body = '<h1>PUT Success</h1>'.encode()
                else:
                    status_line = self.status_line(405)
                    response_body = '<h1>405 Method Not Allowed</h1>'.encode()
                    error_flag = True
            elif os.path.exists(path) and os.path.isdir(path):
                status_line = self.status_line(400)
                response_body = '<h1>400 Bad Request</h1>'.encode()
                error_flag = True
            else:
                status_line = self.status_line(201)
                
                response_body = '<h1>201 Created</h1>'.encode()
                try: 
                    f = open(path,'wb')
                    # if('Content-Encoding' in parsed_headers.keys() and not error_flag):
                    #     content_code ,request_body = ent_head.handle_content_encoding(request_body)
                    #     if(content_code != 200):
                    #         status_line = self.status_line(content_code)
                    #         response_body = generate_error_response(content_code)
                    #         error_flag = True
                    if(not error_flag):
                        f.write(request_body.encode('ISO-8859-1'))
                        ent_head.allow = 'GET, HEAD, POST, PUT, DELETE'
                    f.close()
                    print('created try')
                except FileNotFoundError:
                    directry, file_name = path.rsplit('/',1)
                    print("not found")
                    try:
                        os.makedirs(directry)
                        f = open(path, 'wb')
                        f.write(request_body.encode('ISO-8859-1'))
                        f.close()
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
            print('Error in put', e)
            return 'error in put'.encode(), 0, True

        