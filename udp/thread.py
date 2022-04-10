import threading
import socket
from packet import Packet
import ipaddress


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter, message, routerhost, routerport, serverhost, serverport, conn,
                 isVerbose):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.message = message
        self.routerhost = routerhost
        self.routerport = routerport
        self.serverhost = serverhost
        self.serverport = serverport
        self.conn = conn
        self.isVerbose = isVerbose

    def run(self):
        run_client(self.routerhost, self.routerport, self.serverhost, self.serverport, self.threadID, self.message,
                   self.conn, self.isVerbose)


def run_client(router_addr, router_port, server_addr, server_port, sequence_number, message, conn, isVerbose):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    timeout = 5
    try:
        p = Packet(packet_type=0,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=message.encode("utf-8"))

        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print("Sending packet to Router. Sequence Number = ", p.seq_num)
        conn.settimeout(timeout)
        # print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        verbose_output, response_output = split_verbose_response(p.payload.decode("utf-8"))
        print('Payload: ')
        if isVerbose:
            print(verbose_output, "\r\n")
        print(response_output)

    except socket.timeout:
        print('No response after %d for Packet %d ' % (timeout, p.seq_num))


def split_verbose_response(http_response):
    response_list = http_response.split("\r\n\r\n")
    verbose_output = response_list[0].strip()
    response_output = response_list[1].strip()
    return verbose_output, response_output
