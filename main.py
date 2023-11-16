import random
import hashlib
import mysql.connector                                                                                                                                                  
import os
import threading
from decode-torrent import *
import torrent-generation
seeder_message = None
is_seeder_message_present = False
leecher_message = None
is_leecher_message_present = False
def show_login_menu():
    usernme = input('Enter your username')
    pwd = input('Enter your password: ')
    return usernme, pwd
def show_signup_menu():
    usernme = input('Enter your username: ')
    fullnme = input('Enter your full name: ')
    pwd = input('Enter your password: ')
    return usernme, fullnme, pwd
def seeder(my_socket):
    global seeder_message
    global is_seeder_message_present
    while True:
        while not is_seeder_message_present:
            a = 2
        message = seeder_message
        is_seeder_message_present = False

def receive_thread(my_socket):
    global seeder_message
    global is_seeder_message_present
    global leecher_message
    global is_leecher_message_present
    while True:
        data, addr = my_socket.recvfrom(1000)
        data_list = data.decode().split(':')
        if data_list[0] == 'REQ':
            seeder_message = data.decode()
            is_seeder_message_present = True
        else:
            leecher_message = data.decode()
            is_leecher_message_present = True

def receive_reply(closest_node, my_socket, piece_hash, nodeid, my_ipaddress, portno):
    global leecher_message
    global is_leecher_message_present
    response = None
    while True;
        message = f'REQ:{nodeid}:{my_ipaddress}:{port_no}:{piece_hash}'
        closest_node_ip, closest_node_port, closest_node_id = closest_node
        my_socket.sendto(message.encode(), (closest_node_ip, closest_node_port))
        while not is_leecher_message_present:
            a = 2
        data = leecher_message
        is_leecher_message_present = False
        data_list = data.decode().split(':')
        if data_list[0] == 'RESA':
            closest_node_ip = data_list[5]
            closest_node_port = data_list[6]
            closest_node_id = data_list[4]
        elif data_list[0] == 'RESP':
            response = data_list[4:].join(':')
            break
    return response

def is_all_received(hash_dict):
    return False
def receive_pieces(hashes, routing_table, my_ipaddress, port_no, nodeid, my_socket):
    is_hashpiece_received = {}
    pieces_list = [None for i in range(len(hashes))]
    my_socket.settimeout(2)
    for piece_hash in hashes:
        is_hashpiece_received[piece_hash] = False
    while not is_all_received(is_hashpiece_received):
        random_hash = hashes[random.randint(0, len(hashes))]
        if not is_hashpiece_received[random_hash]:
            closest_node = find_closest_node(random_hash, routing_table)
            if closest_node is None:
                return []
            response = receive_reply(closest_node, my_socket, random_hash, nodeid, my_ipaddress, port_no)
            is_hashpiece_received[random_hash] = True
            print(f'{hashes.index(random_hash)} piece received successfully from someone')
            pieces_list[hashes.index(random_hash)] = response
    return ''.join(pieces_list)



routing_table = {[('192.168.61.203', 23423, '8ff558aaf31aa86ab6b999609f7353a8a2d1d80a')]}
conn = mysql.connector.connect(host='localhost', password='PetronesTower1.', user='root', database='MyDatabase')
cursor = conn.cursor()
print('connection established')
my_ipaddress = input('Enter your ip address: ')
port_no = random.randint(20000, 60000)
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind((my_ipaddress, port_no))
nodeid = hashlib.sha1(f'{my_ipaddress}:{port_no}'.encode()).digest()
username = None
passwd = None
fullname = None
while True:
    print('-----Menu----')
    print('1. Login')
    print('2. Sign up')
    print('3. exit')

    option = int(input('Enter your option: '))
    if option == 1:
        username, passwd = show_login_menu()
        query = 'SELECT exists(SELECT 1 from userInfo where username = %s and passwd = %s)'
        cursor.execute(query, (username, passwd))
        results = cursor.fetchone()
        if results[0]:
            print('Login successful')
            #Construct routing table
            seeder_thread = threading.Thread(target=seeder, args=(my_socket))
            seeder_thread.start()
            receive_thread = threading.Thread(target=receive_thread, args=(my_socket))
            while True:
                cmd = input('Enter command: ')
                if cmd == 'exit':
                    break
                header, filename = cmd.split()
                if header == 'download':
                    if filename in os.listdir():
                        file_info = decode_torrent_file(filename)
                        output_filename = file_info['file-name']
                        hashes = file_info['piece-hashes']
                        no_of_pieces = len(hashes)
                        piece_length = file_info['piece-length']
                        received_file = receive_pieces(hashes, routing_table, my_ipaddress, port_no, nodeid, my_socket)
                        with open(output_filename, 'w') as file:
                            file.write(received_file)
                            print('File received successfully')
                    else:
                        print(f'{filename} not found in the present directory. Please try again.')
                elif header == 'upload':

                else:
                    print('Invalid input. Please try again.')

        else:
            print('Login failed')
    elif option == 2:
        username, fullname, passwd = show_signup_menu()
        query = "SELECT EXISTS(SELECT 1 FROM userInfo WHERE username = %s)"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        exists = result[0]
        if exists:
            print('Username already exists. Please try again.')
        else:
            query = 'INSERT INTO userInfo VALUES(%s, %s, %s)'
            cursor.execute(query, (username, fullname, passwd))
            conn.commit()
            print('Signup successful.')
    else:
        break
