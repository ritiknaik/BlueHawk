from headers import *
import os

class Delete:
    def status_line(self, status_code):
        status = status_codes[status_code]
        line = "HTTP/1.1 %s %s\r\n" % (status_code, status)
        return line.encode()

    def DELETE(self,request):
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
            gen_head = General_Headers(parsed_headers,path)
            req_head = Request_Headers(parsed_headers,path)
            ent_head = Entity_Headers(parsed_headers,path)
            resp_head = Response_Headers(parsed_headers,path)
            error_flag = False
            if(req_head.handle_host() == 400):
                status_line = self.status_line(400)
                response_body = generate_error_response(400)
                ent_head.content_type = "text/html"
                error_flag = True
            if (os.path.exists(path) and os.path.isfile(path) and not error_flag):  
                if not (os.access(path,os.W_OK)):
                    status_line = self.status_line(403)
                    response_body = generate_error_response(403)
                    response_length = len(response_body)
                    error_flag = True
                else:
                    status_line = self.status_line(200)
                    os.unlink(path)
                    response_body = "<h1>File Deleted !</h1>".encode()
                    ent_head.content_type = "text/html"
                    response_length = len(response_body)
            else:
                status_line = self.status_line(404)
                response_body = generate_error_response(404)
                response_length = len(response_body)
                error_flag = True
            ent_head.content_length = response_length
            blank_line = b'\r\n'
            response_headers = gen_head.generate_general_header() + ent_head.generate_entity_headers() + resp_head.generate_response_header()
            response_headers = response_headers.encode()
            pnp = gen_head.handle_connection()
            response = b''.join([status_line, response_headers, blank_line,response_body])
            return response, pnp, False
        except Exception as e:
            print('Error in DELETE',e)
            return "del".encode(), 0, True
    