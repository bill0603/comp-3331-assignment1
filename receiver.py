#This receiver was written by Python3
from socket import *
from helper import packet, parse_packet
import time
import sys

def receiver(port, file):
    server_socket = socket(AF_INET, SOCK_DGRAM) 
    server_socket.bind(('localhost', int(port)))
    #print('The receiver is ready to receive')

    # Make a log file
    log_file = open('Receiver_log.txt', 'a+')

    #Connection setup

    sent_byte_message, address = server_socket.recvfrom(4096)
    receive_syn = parse_packet(sent_byte_message)
    #print('Received a packet')
    if receive_syn.syn and receive_syn.seq == 0:
        p_time = time.time()
        c_time = p_time
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'rcv\t\t{interval}\t\tS\t\t{receive_syn.seq}\t\t{len(receive_syn.payload)}\t\t{receive_syn.ACK}\n'
        log_file.write(log_message)
        #print('Received packet is a syn')
        ACK = receive_syn.seq + 1
        ack_syn = packet(0, ACK, 1, 1, 0, bytes('', encoding = 'utf-8'))
        server_socket.sendto(ack_syn.byte_packet, address)
        #print('Send an ACK packet')
        c_time = time.time()
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'snd\t\t{interval}\t\tSA\t\t{ack_syn.seq}\t\t{len(ack_syn.payload)}\t\t{ack_syn.ACK}\n'
        log_file.write(log_message)
        sent_byte_message, address = server_socket.recvfrom(4096)
        receive_syn_ack = parse_packet(sent_byte_message)
        c_time = time.time()
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'rcv\t\t{interval}\t\tA\t\t{receive_syn_ack.seq}\t\t{len(receive_syn_ack.payload)}\t\t{receive_syn_ack.ACK}\n'
        log_file.write(log_message)
        #print('Received a packet')

    ACK = 1
    seq = 0
    while 1:
        sent_byte_message, address = server_socket.recvfrom(4096)
        sent_packet = parse_packet(sent_byte_message)
        if sent_packet.fin:
            break
        c_time = time.time()
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'rcv\t\t{interval}\t\tD\t\t{sent_packet.seq}\t\t{len(sent_packet.payload)}\t\t{sent_packet.ACK}\n'
        log_file.write(log_message)
        if sent_packet.seq == ACK: 
            ACK = sent_packet.seq + len(sent_packet.payload)
            seq = sent_packet.ACK
            message = str(sent_packet.payload, encoding = 'utf-8')
            f = open(file, 'a+')
            f.write(message)
            f.close()
        ack_packet = packet(seq, ACK, 1, 0, 0, bytes('', encoding = 'utf-8'))
        server_socket.sendto(ack_packet.byte_packet, address)
        c_time = time.time()
        interval = '{:.2f}'.format((c_time - p_time) * 1000)
        log_message = f'snd\t\t{interval}\t\tA\t\t{ack_packet.seq}\t\t{len(ack_packet.payload)}\t\t{ack_packet.ACK}\n'
        log_file.write(log_message)
    
    # Teardown
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'rcv\t\t{interval}\t\tF\t\t{sent_packet.seq}\t\t{len(sent_packet.payload)}\t\t{sent_packet.ACK}\n'
    log_file.write(log_message)
    #print('Received a fin packet')
    fin_ack = packet(sent_packet.ACK, sent_packet.seq + 1, 1, 0, 0, bytes('', encoding = 'utf-8'))
    server_socket.sendto(fin_ack.byte_packet, address)
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'snd\t\t{interval}\t\tA\t\t{fin_ack.seq}\t\t{len(fin_ack.payload)}\t\t{fin_ack.ACK}\n'
    log_file.write(log_message)
    #print('Send a fin ack')
    fin = packet(fin_ack.seq, fin_ack.ACK, 0, 0, 1, bytes('', encoding = 'utf-8'))
    server_socket.sendto(fin.byte_packet, address)
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'snd\t\t{interval}\t\tF\t\t{fin.seq}\t\t{len(fin.payload)}\t\t{fin.ACK}\n'
    log_file.write(log_message)
    #print('Send a fin packet')
    sent_byte_message, address = server_socket.recvfrom(4096)
    #print('Received a packet')
    fin_ack = parse_packet(sent_byte_message)
    c_time = time.time()
    interval = '{:.2f}'.format((c_time - p_time) * 1000)
    log_message = f'rcv\t\t{interval}\t\tA\t\t{fin_ack.seq}\t\t{len(fin_ack.payload)}\t\t{fin_ack.ACK}\n'
    log_file.write(log_message)
    if fin_ack.ACK == fin.seq + 1:
        #print('Teardown successfully')
        server_socket.close()
    log_file.close()

if __name__ == '__main__':
    port = sys.argv[1]
    file = sys.argv[2]
    receiver(port, file)