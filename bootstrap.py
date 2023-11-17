import json
import socket
import trie
import binascii

'''hex_values = [
    "ffffffffffffff0d43e32f1bee18d502791be0e4",
    "d264d67ead367e2418f8904da6b4a26f020ae6a9",
    "90b0095bda5e8bb132924c0b557046fb8459e2c8",
    "8694667eadda24cf239530aecc8497150cd83f56",
]''' 

hex_values = []
# Now you can use this list in your Python code.

def hex_to_binary(hex_string):
    binary_data = binascii.unhexlify(hex_string)
    binary_representation = ''.join(format(byte, '08b') for byte in binary_data)
    return binary_representation

# hex_string = "48656C6C6F2C20576F726C6421"
def string_to_hex(node_id):
    hex_representation = ''.join([format(ord(char), '02X') for char in node_id])
    return hex_representation


info_dict = {}
ip_address = "127.0.0.1"
port = 9000
formatted_values = [[ip_address, port, hex_value] for hex_value in hex_values]

index = 0
formatted_values1 = {}

'''for i in hex_values:
    formatted_values1[i] = formatted_values[index]
    index = index + 1'''

# print(formatted_values)
bootstrap_ip = input("Enter ip: ")
bootstrap_port = input("Enter port: ")

bootstrap_port = int(bootstrap_port)

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.bind((bootstrap_ip, bootstrap_port))

t = trie.Trie()
while(1):
    node_id_str, addr = my_socket.recvfrom(100)
    
    node_id_str = node_id_str.decode() 
    
    # node_id_hex = string_to_hex(node_id_str)
    node_id = hex_to_binary(node_id_str) 
    
    # node_id = "56668c669713d924ea36c2ef893f8b9d0143ccd3"
    #for i in hex_values:
        # j = string_to_hex(i)
       # k = hex_to_binary(i)
        # print(k, end="\n\n")
       # t.insert(k)
    
    # node_id = hex_to_binary(node_id) 
    
    info_node = t.get_bucket_node(node_id)
    # print(info_node)
    t.insert(node_id)
    # print(info_node)
    list_info_node = []
    # print(info_node)
    for i in info_node:
        if i is None:
            list_info_node.append(None)
            continue
        decimal_value = int(i, 2)
        hex_sha1 = hex(decimal_value)[2:]
        temp = formatted_values1[hex_sha1]
        list_info_node.append(temp)
    
    # print(list_info_node)
    info_dict = {}
    prefix = ""
    index = 0
    ind = ""
    for i in node_id:
        # print(i)
        # print(list_info_node[index])
        if index > len(list_info_node)-1:
            break
        prefix += str(t.compliment_index(int(i)))
        ind += i
        if list_info_node[index] is None:
            index = index + 1 
            prefix = ind
            continue
        # print("pre: " + prefix)
        info_dict[prefix] = []
        info_dict[prefix].append(list_info_node[index])
        prefix = ind
        index = index + 1 
    
    node_id = int(node_id, 2)
    node_id = hex(node_id)[2:]
    addr1 = list(addr)
    addr1.append(node_id)
    formatted_values1[node_id] = addr1

    info_dict = str(info_dict)
    
    my_socket.sendto(json.dumps(info_dict).encode(), addr) 
