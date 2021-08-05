#This sender was written by Python3
from socket import *
import sys
import time
import struct
from helper import packet, parse_packet
import math
import random

#sys.setrecursionlimit(200000)
p_time = time.time()
def sender(ip, port, file, mws, mss, timeout, pdrop, seed):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    socket.settimeout(client_socket, timeout / 1000)
    #print('The sender is ready to send')

    # Make a log file
    log_file = open('Sender_log.txt', 'a+')

    # Connection setup
    
    send_syn = packet(0, 0, 0, 1, 0, bytes('', encoding = 'utf-8'))
    address = (ip, port)
    client_socket.sendto(send_syn.byte_packet, address)
    c_time = p_time
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'snd\t\t{interval}\t\tS\t\t{send_syn.seq}\t\t{len(send_syn.payload)}\t\t{send_syn.ACK}\n'
    log_file.write(log_message)
    #print('Sent a syn packet')
    received_byte_message, address = client_socket.recvfrom(4096)
    ack_syn = parse_packet(received_byte_message)
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'rcv\t\t{interval}\t\tSA\t\t{ack_syn.seq}\t\t{len(ack_syn.payload)}\t\t{ack_syn.ACK}\n'
    log_file.write(log_message)
    #print('Received a packet')
    if ack_syn.ACK == 1:
        #print('Received packet is an ACK to syn')
        ack_ack_syn = packet(ack_syn.ACK, ack_syn.seq + 1, 1, 0, 0, bytes('', encoding = 'utf-8'))
        client_socket.sendto(ack_ack_syn.byte_packet, address)
        c_time = time.time()
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'snd\t\t{interval}\t\tA\t\t{ack_ack_syn.seq}\t\t{len(ack_ack_syn.payload)}\t\t{ack_ack_syn.ACK}\n'
        log_file.write(log_message)
        #print('Connection setup successfully')

    # Read message

    f = open(file)
    data_to_send = f.read()
    f.close()
    byte_message = bytes(data_to_send, encoding='utf-8')
    # Break message to mss bytes of payloads
    payload = []
    i = 0
    while i + mss < len(byte_message):
        payload.append(byte_message[i:i + mss])
        i = i + mss
    payload.append(byte_message[i:len(byte_message)])

    # Send message
    window_size = int(mws/mss)
    seq = 1
    ACK = 1
    loss_count = 0
    last_received_ACK = 1
    while len(payload):
        seq, ACK, last_received_ACK = transmission(payload, window_size, seq, ACK, pdrop, address, client_socket, log_file, last_received_ACK, mss, seed)

    # Teardown

    send_fin = packet(last_received_ACK, ACK, 0, 0, 1, bytes('', encoding = 'utf-8'))
    client_socket.sendto(send_fin.byte_packet, address)
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'snd\t\t{interval}\t\tF\t\t{send_fin.seq}\t\t{len(send_fin.payload)}\t\t{send_fin.ACK}\n'
    log_file.write(log_message)
    #print('Sent a fin packet')
    received_byte_message, address = client_socket.recvfrom(4096)
    ack_fin = parse_packet(received_byte_message)
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'rcv\t\t{interval}\t\tA\t\t{ack_fin.seq}\t\t{len(ack_fin.payload)}\t\t{ack_fin.ACK}\n'
    log_file.write(log_message)
    #print('Received a packet')
    if ack_fin.ACK - last_received_ACK == 1:
        #print('Received packet is an ACK to fin')
        received_byte_message, address = client_socket.recvfrom(4096)
        received_fin = parse_packet(received_byte_message)
        c_time = time.time()
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'rcv\t\t{interval}\t\tFA\t\t{received_fin.seq}\t\t{len(received_fin.payload)}\t\t{received_fin.ACK}\n'
        log_file.write(log_message)
        #print('Received a packet')
        if received_fin.fin == 1:
            #print('Received packet is a fin packet')
            ack_received_fin = packet(last_received_ACK, received_fin.seq + 1, 1, 0, 0, bytes('', encoding = 'utf-8'))
            client_socket.sendto(ack_received_fin.byte_packet, address)
            c_time = time.time()
            interval = '{:.2f}'.format((c_time - p_time) * 1000)
            log_message = f'snd\t\t{interval}\t\tA\t\t{ack_received_fin.seq}\t\t{len(ack_received_fin.payload)}\t\t{ack_received_fin.ACK}\n'
            log_file.write(log_message)
            #print('send a fin ack packet')
            #print('Teardown successfully')
            client_socket.close()
    log_file.close()

def transmission(payload, window_size, seq, ACK, pdrop, address, client_socket, log_file, last_received_ACK, mss, seed):
    packet_count = 0
    window_size = min(window_size, len(payload))
    while packet_count < window_size:
        p = packet(seq, ACK, 0, 0, 0, payload[packet_count])
        if random.random() > pdrop:
            ##print('packet is sent')
            client_socket.sendto(p.byte_packet, address)
            c_time = time.time()
            interval = '{:.2f}'.format((c_time - p_time) * 1000)
            log_message = f'snd\t\t{interval}\t\tD\t\t{p.seq}\t\t{len(p.payload)}\t\t{p.ACK}\n'
            log_file.write(log_message)
        else :
            ##print('packet is not sent')
            c_time = time.time()
            interval = '{:.2f}'.format((c_time - p_time) * 1000)
            log_message = f'drop\t{interval}\t\tD\t\t{p.seq}\t\t{len(p.payload)}\t\t{p.ACK}\n'
            log_file.write(log_message)
        seq = seq + len(payload[packet_count])
        packet_count = packet_count + 1

    received_packet_count = 0
    error_count = 0
    while received_packet_count < window_size:
        try:
            received_byte_message, address = client_socket.recvfrom(4096)
            received_packet = parse_packet(received_byte_message)
            c_time = time.time()
            interval = '{:.2f}'.format((c_time - p_time) * 1000)
            log_message = f'rcv\t\t{interval}\t\tA\t\t{received_packet.seq}\t\t{len(received_packet.payload)} \t\t{received_packet.ACK}\n'
            log_file.write(log_message)
            received_packet_count = received_packet_count + 1
            
            index = 0
            if received_packet.ACK - last_received_ACK > 0:
                # Remove received payload
                ack_packet = math.ceil((received_packet.ACK - last_received_ACK) / mss)
                del payload[:ack_packet]
                last_received_ACK = received_packet.ACK
            #else:
            #    error_count = error_count + 1
            #    #print('error', error_count)
            #    if error_count > 1:
            #        #print('start fast re')
            #    # retransmission
            #        seq = last_received_ACK
            #        seq, ACK, last_received_ACK = transmission(payload, window_size, seq, ACK, pdrop, #address, client_socket, log_file, last_received_ACK, mss, seed)
            #        received_packet_count = received_packet_count + window_size

        except OSError:
            #print('in OSError')
            seq = last_received_ACK
            seq, ACK, last_received_ACK = transmission(payload, window_size, seq, ACK, pdrop, address, client_socket, log_file, last_received_ACK, mss, seed)
            received_packet_count = received_packet_count + window_size
    return (seq, ACK, last_received_ACK)

if __name__ == '__main__':
    ip = sys.argv[1]
    port = int(sys.argv[2])
    file = sys.argv[3] 
    mws = int(sys.argv[4])
    mss = int(sys.argv[5])
    timeout = float(sys.argv[6])
    pdrop = float(sys.argv[7])
    seed = int(sys.argv[8])
    random.seed(seed)
    sender(ip, port, file, mws, mss, timeout, pdrop, seed)
