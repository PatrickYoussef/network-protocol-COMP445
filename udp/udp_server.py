import argparse
import socket
import datetime
import argparse
import os

from packet import Packet


def run_server(host, port, verbose, directory):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind((host, port))
        while True:
            print('server is listening at', port)
            data, sender = conn.recvfrom(1024)
            handle_client(conn, data, sender, verbose, directory)
    finally:
        conn.close()


def handle_client(conn, data, sender, verbose, directory):
    try:
        p = Packet.from_bytes(data)
        response = p.payload.decode("utf-8")

        print("Router: ", sender)
        print("Packet: ", p)
        if p.packet_type == 0:
            print("The packet type received is, " + str(p.packet_type))
            print("Payload: ", response)

            query = readQuery(response, directory, verbose)

            print("Server to send the following response:\r\n", query)
            p.payload = query.encode("utf-8")
            conn.sendto(p.to_bytes(), sender)

        if p.packet_type == 1:
            print("Packet type: ", str(p.packet_type), "(SYN)")

            p.packet_type = 2
            p.payload = "SYN received, here is SYN_ACK".encode("utf-8")
            print("SYN received, I will send SYN_ACK")
            conn.sendto(p.to_bytes(), sender)

        if p.packet_type == 3:
            print("Packet type: ", str(p.packet_type), "(ACK)")
            p.packet_type == 3
            p.payload = "ACK received, I will send ACK".encode("utf-8")
            print("ACK received, I will send ACK")
            conn.sendto(p.to_bytes(), sender)

    except Exception as e:
        print("Error: ", e)


def three_way_handshake(conn):
    print("Udp Server waiting for 3-way handshake with client")
    try:
        data, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(data)
        print("Router: ", sender)
        print("Packet: ", p)
        p_to_send = Packet(packet_type=1,
                           seq_num=0,
                           peer_ip_addr=p.peer_ip_addr,
                           peer_port=p.peer_port,
                           payload="".encode("utf-8"))
        conn.sendto(p_to_send.to_bytes(), sender)
    except Exception as e:
        print("Error: ", e)


def readQuery(query, directory, verbose):
    queryList = query.split("\r\n")
    request_type = queryList[0].split(' ')[0]
    fileName = queryList[0].split(' ')[1]
    headers = get_all_content_headers(query, request_type)
    if '.py' in fileName or '.md' in fileName:
        print('HTTP Error 400: Access Restrictions. You cannot read or write this file') if verbose else ''
        return format_verbose(headers,
                              'HTTP Error 400: Access Restrictions. You cannot read or write this file\r\n') + "\r\nPlease try again"
    if request_type == 'GET':
        if queryList[0].split(' ')[1] == '/':
            list_of_files = getListOfFiles(directory)
            client_query = "The files in the directory " + directory + " are the following:\r\n"
            for file in list_of_files:
                client_query += os.path.basename(os.path.normpath(file))
                client_query += "\r\n"
            print('HTTP/1.0 200 OK') if verbose else ''
            full_query = format_verbose(headers, 'HTTP/1.0 200 OK\r\n') + "\r\n" + client_query
            return full_query.strip()
        else:
            fileName = queryList[0].split(' ')[1]
            fileContent = readFileContent(fileName, directory, query, verbose)
            return fileContent
    if request_type == 'POST':
        fileName = queryList[0].split(' ')[1]
        if fileName == '/':
            print('HTTP ERROR 404: You need to append a file name to the request') if verbose else ''
            full_query = format_verbose(headers,
                                        "HTTP ERROR 404: You need to append a file name to the request\r\n") + "\r\nHTTP ERROR 404: Please retry"
            return full_query
        query_body = get_query_body(queryList)
        res = writeFile(fileName, directory, query_body, query, verbose)
        return res
    return request_type


def get_query_body(queryList):
    counter = 0
    for line in queryList:
        if line == '':
            break
        counter = counter + 1
    body_index = counter + 1
    return queryList[body_index]


def writeFile(fileName, directory, query_body, query, verbose):
    if directory == '/':
        fileName = fileName[1:]
    file_to_write = directory[1:] + fileName
    if '/' in file_to_write:
        os.makedirs(os.path.dirname(file_to_write), exist_ok=True)
    headers = get_all_content_headers(query, 'POST')
    try:
        f = open(file_to_write, 'w')
    except OSError:
        print("HTTP ERROR 404: Could not write to file: " + file_to_write + "\r\n") if verbose else ''
        full_query = format_verbose(headers,
                                    "HTTP ERROR 404: Could not write to file: " + file_to_write + "\r\n") + "\r\nHTTP ERROR 404: Please retry"
        return full_query
    f.write(query_body)
    print('HTTP 200 OK') if verbose else ''
    res = format_verbose(headers, "HTTP 200 OK\r\n") + "\r\n" + query_body
    return res


def readFileContent(fileName, directory, query, verbose):
    headers = get_all_content_headers(query, 'GET')
    if directory == '/':
        fileName = fileName[1:]
    file_to_open = directory[1:] + fileName
    try:
        f = open(file_to_open, 'r')
    except OSError:
        print("HTTP ERROR 404: Could not read file: " + file_to_open + "\r\n") if verbose else ''
        return format_verbose(headers,
                              "HTTP ERROR 404: Could not read file: " + file_to_open + "\r\n") + "\r\nHTTP ERROR 404: Please retry"
    file_data = f.read()
    print('HTTP/1.0 200 OK') if verbose else ''
    response = format_verbose(headers, 'HTTP/1.0 200 OK\r\n') + "\r\n" + file_data
    return response


def getListOfFiles(directory):
    files_list = []
    path = os.getcwd().replace("\\", "/") + directory + "/"
    for filename in os.listdir(path):
        f = os.path.join(filename)
        absolute_path = path + f
        if os.path.isfile(absolute_path) and '.py' not in f:
            files_list.append(absolute_path)
    return files_list


def get_all_content_headers(query, request_type):
    query_list = query.split("\r\n")
    headers = ""
    if request_type != 'POST':
        headers = "Content-Length: " + str(len(query)) + "\r\n"
    for line in query_list[2:]:
        headers += line
        headers += "\r\n"
        if line == '':
            break
    return headers.strip()


def format_verbose(headers, status_code):
    verbose = ""
    verbose += status_code
    verbose += datetime.datetime.now().strftime("%c") + "\r\n"
    verbose += headers
    verbose += '\r\n'
    return verbose


# Usage python udp_server.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="echo server port", type=int, default=8007)
parser.add_argument("-v", action='store_true', help='verbose')
parser.add_argument("-d", help="directory", default='/')
args = parser.parse_args()
run_server('', args.port, args.v, args.d)
