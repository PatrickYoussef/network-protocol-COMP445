import argparse
import ipaddress
import socket
import sys
import json
import urllib.parse

from packet import Packet

request_types = ['get', 'post']


def handle_client(router_addr, router_port, server_addr, server_port, request, URL, verbose, headers_list, file, data_body):
    if request == request_types[0]:
        if file is not None or data_body is not None:
            print(500, "Get operation cannot contain -f or -d")
            sys.exit()
        run_request(router_addr, router_port, server_addr, server_port, request_types[0], verbose, headers_list, None, URL)
    elif request == request_types[1]:
        if data_body is None and file is None:
            print(500, "Post operation needs to include -d or -f. Write --help for more information")
        if data_body is not None:
            run_request(router_addr, router_port, server_addr, server_port, request_types[1], verbose, headers_list, str(data_body), URL)
        if file is not None:
            try:
                f = open(file)
            except OSError:
                print("Could not open/read file:", file)
                sys.exit()
            file_data = json.load(f)
            formatted_data = json.dumps(file_data)
            run_request(router_addr, router_port, server_addr, server_port, request_types[1], verbose, headers_list, formatted_data, URL)


def run_request(router_addr, router_port, server_addr, server_port, request_type, isVerbose, headers_list, data, URL):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    parsedUrl = urllib.parse.urlparse(URL)
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:
        msg = build_query(request_type, parsedUrl, headers_list, data)
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=msg.encode("utf-8"))
        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print('Send "{}" to router'.format(msg))

        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        verbose_output, response_output = split_verbose_response(p.payload.decode("utf-8"))
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ')
        if isVerbose:
            print(verbose_output, "\r\n")
        print(response_output)

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close()
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


# Usage:
# python echoclient.py --routerhost localhost --routerport 3000 --serverhost localhost --serverport 8007

# -f file name and -d body request are mutually exclusive
header_file_parser = argparse.ArgumentParser(add_help=False)
group = header_file_parser.add_mutually_exclusive_group()
group.add_argument('-f', help='file name')
group.add_argument('-d', help='body request')

parser = argparse.ArgumentParser(prog='udp_client', conflict_handler='resolve', parents=[header_file_parser])
parser.add_argument('request', choices=['get', 'post'], default='get', help='GET or POST')
parser.add_argument('URL', default='www.python.org', help='server host')
parser.add_argument('-v', action='store_true', help='verbose')
parser.add_argument('-h', nargs='*', action='extend', help='headers')

parser.add_argument("--routerhost", help="router host", default="localhost")
parser.add_argument("--routerport", help="router port", type=int, default=3000)

parser.add_argument("--serverhost", help="server host", default="localhost")
parser.add_argument("--serverport", help="server port", type=int, default=8007)
args = parser.parse_args()

handle_client(args.routerhost, args.routerport, args.serverhost, args.serverport, args.request, args.URL, args.v, args.h, args.f, args.d)
