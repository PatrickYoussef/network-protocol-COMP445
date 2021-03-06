import json
import socket
import argparse
import sys
import urllib.parse

request_types = ['get', 'post']


def run_client(request, URL, verbose, headers_list, file, data_body):
    if request == request_types[0]:
        if file is not None or data_body is not None:
            print(500, "Get operation cannot contain -f or -d")
            sys.exit()
        run_request(request_types[0], verbose, headers_list, None, URL)
    elif request == request_types[1]:
        if data_body is None and file is None:
            print(500, "Post operation needs to include -d or -f. Write --help for more information")
        if data_body is not None:
            run_request(request_types[1], verbose, headers_list, str(data_body), URL)
        if file is not None:
            try:
                f = open(file)
            except OSError:
                print("Could not open/read file:", file)
                sys.exit()
            file_data = json.load(f)
            formatted_data = json.dumps(file_data)
            run_request(request_types[1], verbose, headers_list, formatted_data, URL)


def run_request(request_type, isVerbose, headers_list, data, URL):
    parsedUrl = urllib.parse.urlparse(URL)
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = parsedUrl.netloc.split(":")[1]
    try:
        socket_client.connect(('localhost', int(port)))
        query = build_query(request_type, parsedUrl, headers_list, data)
        socket_client.sendall(query.encode("utf-8"))
        http_response = socket_client.recv(4096)
        verbose_output, response_output = split_verbose_response(http_response.decode())
        if isVerbose:
            print(verbose_output, "\r\n")
        print(response_output)
    except:
        print("connection failed")
    finally:
        socket_client.close()
        print("connection closed.")


def split_verbose_response(http_response):
    response_list = http_response.split("\r\n\r\n")
    verbose_output = response_list[0].strip()
    response_output = response_list[1].strip()
    return verbose_output, response_output


def build_query(request_type, parsedUrl, headers_list, data):
    params = ""
    if parsedUrl.query:
        params = "?" + parsedUrl.query
    query = request_type.upper() + " " + parsedUrl.path + params + " HTTP/1.0\r\n" + "Host: " + parsedUrl.netloc + "\r\n"
    if headers_list is not None:
        for header in headers_list:
            query += (header + "\r\n")
    if request_type == 'post':
        query += "Content-Length: " + str(len(data))
        query += ("\r\n\r\n" + data)
    query += "\r\n\r\n"
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
