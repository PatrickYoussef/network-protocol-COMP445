import socket
import argparse
import threading

request_types = ['get', 'post']


def run_client(request, URL, verbose, headers_list, file, data_body):
    if request == request_types[0]:
        if file is not None or data_body is not None:
            print("it fails !")
        run_request(request_types[0], verbose, headers_list, data_body, file, URL)
    elif request == request_types[1]:
        run_request(request_types[1], verbose, headers_list, data_body, file, URL)
    # socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # request_type = query.split()[0]
    # try:
    #     socket_client.connect((host, 80))
    #     socket_client.send(query.encode())
    #     http_response = socket_client.recv(1024)
    #     print(http_response.decode())
    # finally:
    #     socket_client.close()


def run_request(request_type, isVerboseEnabled, headers_list, data_request, file_name, URL):
    print(request_type, isVerboseEnabled, headers_list, data_request, file_name, URL)


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
