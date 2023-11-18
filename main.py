import random
import ast
import hashlib
import mysql.connector                                                                                                                                                  
import os
import threading
from decode_torrent import *
from torrent_generation import *
import time
import json
seeder_message = None
is_seeder_message_present = False
leecher_message = None
is_leecher_message_present = False
files_dict = {}


def show_login_menu():
    usernme = input('Enter your username: ')
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
#        update_routing_table()
        message_list = message.split(':')
        leecher_node_id = message_list[1]
        leecher_ip_address = message_list[2]
        leecher_port_no = int(message_list[3])#added
        update_routing_table([leecher_node_id, leecher_ip_address, leecher_port_no], nodeid)
        file_name = message_list[4]
        hash_value = message_list[5]
        if file_name in files_dict:
            file_data = files_dict[filename]
            if hash_value in file_data:
                piece_data = file_data[hash_value]
                response_message = f'RESP:{nodeid}:{ip_address}:{port_no}:{file_name}:{piece_data}'
                my_socket.sendto(response_message.encode(), (leecher_ip_address, leecher_port_no))
            else:
                next_closest_bucket = find_closest_node(hash_value)
                next_closest_node = next_closest_bucket[random.randint(0, len(next_closest_bucket) - 1)]
                response_message = f'RESA:{nodeid}:{ip_address}:{port_no}:{file_name}:{next_closest_node[0]}:{next_closest_node[1]}:{next_closest_node[2]}'
                my_socket.sendto(response_message.encode(), (leecher_ip_address, leecher_port_no))
        else:
                next_closest_bucket = find_closest_node(hash_value)
                next_closest_node = next_closest_bucket[random.randint(0, len(next_closest_bucket) - 1)]
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
def update_routing_table(node, mynode_id):
    global routing_table
    mynodeid_bin = bin(int(mynode_id, 16))[2:]
    node_id_bin = bin(int(node[0], 16))[2:]
    if mynodeid_bin == node_id_bin:
        print('my node id same as the one provided. Not updating routing table')
        return
    prefix = ''
    i = 0
    while i <  len(node_id_bin):
        if mynodeid_bin[i] == node_id_bin[i]:
            prefix += node_id_bin[i]
        else:
            break
        i += 1
    prefix += node_id_bin[i]
    append_node = [node[1], int(node[2]), node[0]]
    if prefix in routing_table:
        if append_node in routing_table[prefix]:
            print('node already present. Not updating routing table')
            return
        routing_table[prefix].append([node[1], int(node[2]), node[0]])
        print('appending node in routing table')
    else:
        routing_table[prefix] = [[node[1], int(node[2]), node[0]]]
        print('creating entry for node in routing table')
    return


def receive_reply(closest_node, my_socket, piece_hash, nodeid, my_ipaddress, portno,file_name):
    global leecher_message
    global is_leecher_message_present
    response = None
    closest_node_ip = None
    closest_node_port = None
    closest_node_id = None
    closest_node_ip, closest_node_port, closest_node_id = closest_node
    while True:
        message = f'REQ:{nodeid}:{my_ipaddress}:{port_no}:{file_name}:{piece_hash}'
        print(f'requesting for {piece_hash} to {closest_node_ip}:{closest_node_port}')
        my_socket.sendto(message.encode(), (closest_node_ip, closest_node_port))
        start_time = time.time()
        time_difference = 0
        while not is_leecher_message_present:
            time_difference = time.time() - start_time
            if time_difference >= 2:
                break
            a = 2
        if time_difference >= 2:
            is_leecher_message_present = False
            print('timeout')
            return ''
        data = leecher_message
        data = data
        is_leecher_message_present = False
        data_list = data.split(':')
        if data_list[0] == 'RESA':
            print(f'resa response received from {closest_node_ip}')
            closest_node_ip = data_list[5]
            closest_node_port = int(data_list[6])
            closest_node_id = data_list[7]
            print(f'forwarding to {closest_node_ip}:{closest_node_port}')
            if closest_node_id == nodeid:
                print('returning empty string')
                return ''
        elif data_list[0] == 'RESP':
            print(f'peice received from {closest_node_ip}')
            response = ':'.join(data_list[5:])
            update_routing_table(data_list[1:4], nodeid)
            break
    return response

def is_all_received(hash_dict):
    for key in hash_dict:
        if hash_dict[key] == False:
            return False

    return True

def get_routing_table(node_id, my_socket):
    bootstrap_ip = "192.168.193.203"
    bootstrap_port_no = 20000
    message = node_id
    my_socket.sendto(message.encode(), (bootstrap_ip, bootstrap_port_no))
    data, addr = my_socket.recvfrom(1000)
    return data.decode()

def find_closest_node(random_hash):
    global routing_table
    if len(routing_table) > 0:
        return random.choice(list(routing_table.values()))
    else:
        return None
    min_hash_value = 234253
    min_node = None
    min_key = None
    for key in routing_table:
        if min_node is None:
            if len(routing_table[key]):
                min_hash_value = int(random_hash, 16) ^ int(routing_table[key][0][2], 16)
                min_node = routing_table[key][0]
                min_key = key
                print('Initial Metric', min_hash_value)
        else:
            if len(routing_table[key]):
                current_hash_value = int(random_hash, 16) ^ int(routing_table[key][0][2], 16)
                if current_hash_value < min_hash_value:
                    min_hash_value = current_hash_value
                    min_node = routing_table[key][0]
                    min_key = key
                    print('updated Metric', min_hash_value)
    if not min_key:
        print('returning none')
        return None
    print('return closest node metric - ', min_hash_value)
    return routing_table[min_key]

def receive_pieces(hashes, my_ipaddress, port_no, nodeid, my_socket, file_name):
    global routing_table#added
    global seeder_port
    is_hashpiece_received = {}
    pieces_list = [None for i in range(len(hashes))]
    for piece_hash in hashes:
        is_hashpiece_received[piece_hash] = False
    while not is_all_received(is_hashpiece_received):
        random_hash = hashes[random.randint(0, len(hashes) - 1)]
        if not is_hashpiece_received[random_hash]:
            closest_bucket = find_closest_node(random_hash)
            closest_node = closest_bucket[random.randint(0, len(closest_bucket) - 1)]
            
            #closest_node = ['127.0.0.1', seeder_port, hashlib.sha1(f'127.0.0.1:{seeder_port}'.encode()).digest().hex()]
            print('closest node', closest_node)
            if closest_node is None:
                return None
            response = receive_reply(closest_node, my_socket, random_hash, nodeid, my_ipaddress, port_no,file_name)
            if response != '':
                is_hashpiece_received[random_hash] = True
                print(f'{hashes.index(random_hash)} piece received successfully from someone')
                pieces_list[hashes.index(random_hash)] = response
    return ''.join(pieces_list)

#seeder_port = int(input('Enter seeder port: '))
conn = mysql.connector.connect(host='localhost', password='PetronesTower1.', user='root', database='MyDatabase')
cursor = conn.cursor()
print('connection established')
my_ipaddress = input('Enter your ip address: ')
port_no = random.randint(20000, 60000)
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind((my_ipaddress, port_no))
print('my port no - ', port_no)
nodeid = hashlib.sha1(f'{my_ipaddress}:{port_no}'.encode()).digest().hex()
username = None
passwd = None
fullname = None
routing_table = None
while True:
    print('-----Menu----')
    print('1. Login')
    print('2. Sign up')
    print('3. exit')

    option = int(input('Enter your option: '))
    if option == 1:
#        username, passwd = show_login_menu()
#        query = 'SELECT exists(SELECT 1 from userInfo where username = %s and passwd = %s)'
#        cursor.execute(query, (username, passwd))
#        results = cursor.fetchone()
#        if results[0]:
        if True:
            print('Login successful')
            #Construct routing table
            route_table1 = get_routing_table(nodeid, my_socket)
            print(route_table1)
            print(type(route_table1))
            r = json.loads(route_table1)
            routing_table = ast.literal_eval(r)
            print(type(routing_table))
            print(routing_table)
            seeder_thread = threading.Thread(target=seeder, args=(my_socket,my_ipaddress,port_no,nodeid))
            seeder_thread.start()
            receive_thread = threading.Thread(target=receive_thread, args=(my_socket,))
            receive_thread.start()
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
                        received_file = receive_pieces(hashes, my_ipaddress, port_no, nodeid, my_socket,output_filename)
                        if received_file is not None:
                            with open(output_filename + 'copy', 'w') as file:
                                file.write(received_file)
                                print('File received successfully')
                        else:
                            print('Routing table empty. No info about peers.')
                    else:
                        print(f'{filename} not found in the present directory. Please try again.')
                elif header == 'upload':
                    if filename in os.listdir():
                        torrent_file = create_torrent_file(filename, 256)
                    
                        with open(filename, 'r') as file:
                            file_data = file.read()
                            files_dict[filename] = {}
                            for i in range(0, len(file_data), 256):
                                if i + 256 < len(file_data):#added
                                    piece_data = file_data[i:i + 256]
                                else:
                                    piece_data = file_data[i:]
                                    print(type(piece_data))
                                #piece_hash = hashlib.sha1(piece_data.encode()).digest().hex()#added
                                piece_hash = hashlib.sha1(piece_data.encode()).digest().hex()#added
                                files_dict[filename][piece_hash] = piece_data#added
                        print('File uploaded successfully')
                        print(files_dict[filename])
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
