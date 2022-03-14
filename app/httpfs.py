import json
import socket
import sys
import threading
import argparse
import os


def run_server(host, port, verbose, directory):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(5)
        print('The server is ready to receive at port', port)
        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_client, args=(conn, addr, verbose, directory)).start()
    finally:
        listener.close()


def handle_client(conn, addr, verbose, directory):
    print('New client from', addr)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            query = readQuery(data.decode(), directory)
            conn.sendall(query.encode("utf-8"))
    finally:
        print("Connection with client from", addr, "is now closed")
        conn.close()


def readQuery(query, directory):
    queryList = query.split("\r\n")
    request_type = queryList[0].split(' ')[0]
    if request_type == 'GET':
        if queryList[0].split(' ')[1] == '/':
            list_of_files = getListOfFiles(directory)
            query = "The files in the directory " + directory + " are the following:\r\n"
            for file in list_of_files:
                query += os.path.basename(os.path.normpath(file))
                query += "\r\n"
            return query
        else:
            fileName = queryList[0].split(' ')[1]
            fileContent = readFileContent(fileName, directory, getListOfFiles(directory))
            print(fileContent)
            return fileContent
    if request_type == 'POST':
        print(queryList[0].split(' ')[1])
    return request_type


def readFileContent(fileName, directory, list_of_files):
    # real_file = ""
    # for file in list_of_files:
    #     shortened_file = os.path.basename(os.path.normpath(file))
    #     if fileName[1:] == shortened_file:
    #         real_file = shortened_file
    #         break
    if directory == '/':
        fileName = fileName[1:]
    file_to_open = directory[1:] + fileName
    try:
        f = open(file_to_open, 'r')
    except OSError:
        return "HTTP ERROR 404: Could not open/read file: " + file_to_open
    # if '.json' in fileName:
    #     file_data = json.load(f)
    #     formatted_data = json.dumps(file_data)
    #     return formatted_data
    file_data = f.read()
    return file_data


def getListOfFiles(directory):
    files_list = []
    path = os.getcwd().replace("\\", "/") + directory + "/"
    for filename in os.listdir(path):
        f = os.path.join(filename)
        absolute_path = path + f
        if os.path.isfile(absolute_path) and '.py' not in f:
            files_list.append(absolute_path)
    return files_list


# Usage python httpfs.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("-v", action='store_true', help='verbose')
parser.add_argument("-p", help="port", type=int, default=8080)
parser.add_argument("-d", help="directory", default='/')
args = parser.parse_args()
run_server('', args.p, args.v, args.d)
