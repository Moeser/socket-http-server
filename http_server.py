import socket
import sys
import traceback
import os
import mimetypes

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """
    resp = b"HTTP/1.1 200 OK\r\nContent-Type: " + mimetype + b"\r\n\r\n" + body

    return resp

def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"HTTP/1.1 405 Method Not Allowed\r\n\r\nMethod Not Allowed\r\n"


def response_not_found():
    """Returns a 404 Not Found response"""

    return b"HTTP/1.1 404 Not Found\r\n\r\nNot Found.\r\n"


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """

    m, p, v = request.split("\r\n")[0].split(" ")
    if request[0:3] != 'GET':
        raise NotImplementedError
    return p

def response_path(path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    content = b"not implemented"
    mime_type = b"not implemented"

    web_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webroot')
    req_path = os.path.normpath('/'.join([web_path, path]))
    if not os.path.exists(req_path):
        raise NameError

    if os.path.isdir(req_path):
        files_list = "\r\n".join(os.listdir(req_path))
        content = files_list.encode('utf-8')
        mime_type = b"text/plain"
    else:
        with open(req_path, 'rb') as fi:
            content = fi.read()
        mime_type = mimetypes.guess_type(req_path)[0].encode('utf-8')

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break
		

                print("Request received:\n{}\n\n".format(request))

                try:
                    path = parse_request(request)
                    content, mimetype = response_path(path)
                    response = response_ok(body=content, mimetype=mimetype)
                except NotImplementedError:
                    response = response_method_not_allowed()
                except NameError:
                    response = response_not_found()

                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close() 

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


