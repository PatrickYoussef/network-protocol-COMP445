import socket
import argparse
import sys
import urllib.parse

request_types = ['get', 'post']

get_headers = """\
GET {path} HTTP/1.0\r
Host: {host}\r
\r\n"""

post_headers = """\
POST {path} HTTP/1.0\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""


def run_client(request, URL, verbose, headers_list, file, data_body):
    if request == request_types[0]:
        if file is not None or data_body is not None:
            print(500, "Get operation cannot contain -f or -d")
            sys.exit()
        run_request(request_types[0], verbose, headers_list, data_body, file, URL)
    elif request == request_types[1]:
        run_request(request_types[1], verbose, headers_list, data_body, file, URL)


def get_request(isVerbose, headers_list, URL):
    parsedUrl = urllib.parse.urlparse(URL)
    print(isVerbose, headers_list, URL, parsedUrl)
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_client.connect(('httpbin.org', 80))
        query = "GET "
        socket_client.send(b'GET /status/418 HTTP/1.0\r\nHost: httpbin.org\r\n\r\n')
        http_response = socket_client.recv(1024)
        isVerbose and print(http_response.decode())
    except:
        print("connection failed")
    finally:
        socket_client.close()
        print("connection closed.")


def run_request(request_type, isVerbose, headers_list, data_request, file_name, URL):
    print(request_type, isVerbose, headers_list, data_request, file_name, URL)
    parsedUrl = urllib.parse.urlparse(URL)
    print(parsedUrl)
    params_list = parse_parameters(parsedUrl.query)
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_client.connect((parsedUrl.netloc, 80))
        query = build_query(request_type, parsedUrl, headers_list, data_request)
        print(query)
        socket_client.send(query.encode())
        http_response = socket_client.recv(4096)
        isVerbose and print(http_response.decode())
    except:
        print("connection failed")
    finally:
        socket_client.close()
        print("connection closed.")


def parse_parameters(params):
    params_list = urllib.parse.parse_qs(params)
    params_dict = {k: v[0] for k, v in params_list.items()}
    return params_dict


def build_query(request_type, parsedUrl, headers_list, data):
    params = ""
    if parsedUrl.query:
        params = "?" + parsedUrl.query
    query = request_type.upper() + " " + parsedUrl.path + params + " HTTP/1.0\r\n" + "Host: " + parsedUrl.netloc + "\r\n"
    for header in headers_list:
        query += (header + "\r\n")
    # if request_type == 'post':
    #     query += request_type.upper() + " " + parsedUrl.path + " "
    query += "\r\n"
    return query


# -f file name and -d body request are mutually exclusive
header_file_parser = argparse.ArgumentParser(add_help=False)
group = header_file_parser.add_mutually_exclusive_group()
group.add_argument('-f', help='file name')
group.add_argument('-d', help='body request')

# write --help to get all documentation
parser = argparse.ArgumentParser(prog='httpc', conflict_handler='resolve', parents=[header_file_parser])
parser.add_argument('request', choices=['get', 'post'], default='get', help='GET or POST')
parser.add_argument('URL', default='www.python.org', help='server host')
parser.add_argument('-v', action='store_true', help='verbose')
parser.add_argument('-h', nargs='*', action='extend', help='headers')
args = parser.parse_args()
run_client(args.request, args.URL, args.v, args.h, args.f, args.d)
