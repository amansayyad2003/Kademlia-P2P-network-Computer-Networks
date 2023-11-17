import random
import hashlib
import mysql.connector                                                                                                                                                  
import os
import threading
from decode-torrent import *
from torrent-generation import *
import time
seeder_message = None
is_seeder_message_present = False
leecher_message = None
is_leecher_message_present = False
files_dict = {}


def show_login_menu():
    usernme = input('Enter your username')
    pwd = input('Enter your password: ')
    return usernme, pwd


def show_signup_menu():
    usernme = input('Enter your username: ')
    fullnme = input('Enter your full name: ')
    pwd = input('Enter your password: ')
    return usernme, fullnme, pwd


def seeder(my_socket,ip_address,port_no,nodeid):
    global seeder_message
    global files_dict
    global is_seeder_message_present
    global routing_table#added to find the closest node
    while True:
        while not is_seeder_message_present:
            a = 2
        message = seeder_message
        is_seeder_message_present = False
        # update routing table 
        message_list = message.split(':')
        leecher_node_id = message_list[1]
        leecher_ip_address = message_list[2]
        leecher_port_no = int(message_list[3])#added
        file_name = message_list[4]
        hash_value = message_list[5]
        file_data = files_dict[filename]
        if hash_value in file_data:
            piece_data = file_data[hash_value]
            response_message = f'RESP:{nodeid}:{ip_address}:{port_no}:{piece_data}'
            my_socket.sendto(response_message.encode(), (leecher_ip_address, leecher_port_no))
        else:
            next_closest_node = closest_node()
            response_message = f'RESA:{nodeid}:{ip_address}:{port_no}:{file_name}:{next_closest_node[0]}:{next_closest_node[1]}:{next_closest_node[2]}'
            my_socket.sendto(response_message.encode(), (leecher_ip_address, leecher_port_no))
        


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

def receive_reply(closest_node, my_socket, piece_hash, nodeid, my_ipaddress, portno,file_name):
    global leecher_message
    global is_leecher_message_present
    response = None
    while True:
        message = f'REQ:{nodeid}:{my_ipaddress}:{port_no}:{file_name}:{piece_hash}'
        closest_node_ip, closest_node_port, closest_node_id = closest_node
        my_socket.sendto(message.encode(), (closest_node_ip, closest_node_port))
        start_time = time.time()
        time_difference = 0
        while not is_leecher_message_present:
            time_difference = time.time() - start_time
            if time_difference >= 2:
                break
            a = 2
        if time_difference >= 2:
            return ''
        data = leecher_message
        is_leecher_message_present = False
        data_list = data.decode().split(':')
        if data_list[0] == 'RESA':
            closest_node_ip = data_list[6]
            closest_node_port = data_list[7]
            closest_node_id = data_list[5]
        elif data_list[0] == 'RESP':
            response = data_list[5:].join(':')
            break
    return response

def is_all_received(hash_dict):
    for key in hash_dict:
        if hash_dict[key] == False:
            return False

    return True

def find_closest_node(random_hash):
    global routing_table
    min_hash_value = 234253
    min_node = None
    for key in routing table:
        if min_node is None:
            if len(routing_table[key]):
            min_hash_value = int(random_hash, 16) ^ int(routing_table[key][0][2], 16)
            min_node = routing_table[key][0]
        else:
            if len(routing_table[key]):
                current_hash_value = int(random_hash, 16) ^ int(routing_table[key][0][2], 16)
                if current_hash_value < min_hash_value:
                    min_hash_value = current_hash_value
                    min_node = routing_table[key][0]
    return min_node

def receive_pieces(hashes, my_ipaddress, port_no, nodeid, my_socket, file_name):
    global routing_table#added
    is_hashpiece_received = {}
    pieces_list = [None for i in range(len(hashes))]
    for piece_hash in hashes:
        is_hashpiece_received[piece_hash] = False
    while not is_all_received(is_hashpiece_received):
        random_hash = hashes[random.randint(0, len(hashes))]
        if not is_hashpiece_received[random_hash]:
            closest_node = find_closest_node(random_hash)
            if closest_node is None:
                return None
            response = receive_reply(closest_node, my_socket, random_hash, nodeid, my_ipaddress, port_no,file_name)
            if response != '':
                is_hashpiece_received[random_hash] = True
                print(f'{hashes.index(random_hash)} piece received successfully from someone')
                pieces_list[hashes.index(random_hash)] = response
    return ''.join(pieces_list)



routing_table = {'0': [['192.168.61.203', 23423, '8ff558aaf31aa86ab6b999609f7353a8a2d1d80a']]}
conn = mysql.connector.connect(host='localhost', password='PetronesTower1.', user='root', database='MyDatabase')
cursor = conn.cursor()
print('connection established')
my_ipaddress = input('Enter your ip address: ')
port_no = random.randint(20000, 60000)
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind((my_ipaddress, port_no))
nodeid = hashlib.sha1(f'{my_ipaddress}:{port_no}'.encode()).digest().hex()
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
            seeder_thread = threading.Thread(target=seeder, args=(my_socket,my_ipaddress,port_no,nodeid))
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
                        received_file = receive_pieces(hashes, routing_table, my_ipaddress, port_no, nodeid, my_socket,output_filename)
                        with open(output_filename, 'w') as file:
                            file.write(received_file)
                            print('File received successfully')
                    else:
                        print(f'{filename} not found in the present directory. Please try again.')
                elif header == 'upload':
                    if filename in os.listdir():
                        torrent_file = torrent-generation.create_torrent_file(filename, 256)
                    
                        with open(filename, 'rb') as file:
                            file_data = file.read()
                            files_dict[filename] = {}
                            for i in range(0, len(file_data), 256):
                                if i + 256 < len(file_data):#added
                                    piece_data = file_data[i:i + 256]
                                else:
                                    piece_data = file_data[i:]
                                piece_hash = hashlib.sha1(piece_data.encode()).digest().hex()#added
                                files_dict[filename][piece_hash] = piece_data#added
                    else:
                        print('file does not exist. try again !!')

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
