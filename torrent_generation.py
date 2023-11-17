import hashlib
import bencodepy
import time
import socket

def get_local_ip():
    try:
        # This may not always return the external IP, especially if behind a router.
        ip = socket.gethostbyname(socket.gethostname())
        return ip
    except:
        return 'Unknown'

def calculate_md5(file_data):
    md5 = hashlib.md5()
    md5.update(file_data)
    return md5.hexdigest()


def calculate_piece_hashes(file_data, piece_size):
    piece_hashes = []
    for i in range(0, len(file_data), piece_size):
        piece_data = file_data[i:i + piece_size]
        piece_hashes.append(hashlib.sha1(piece_data).digest())
    return piece_hashes

def create_torrent_file(file_path, piece_size):
    # Read file information
    with open(file_path, 'rb') as file:
        file_data = file.read()
        file_size = len(file_data)
        file_name = file_path.split('/')[-1]  # Extract file name from the path

    # Calculate piece hashes
    piece_hashes = calculate_piece_hashes(file_data, piece_size)

    md5sum = calculate_md5(file_data)
    local_ip = get_local_ip()


    # Create dictionary with torrent metadata
    torrent_info = {
        'info': {
            'length': file_size,
            'name': file_name,
            'piece length': piece_size,
            'pieces': b'/'.join(piece_hashes),
            'md5sum': md5sum,
        },
        'created by': f'Your Torrent Generator - {local_ip}',
        'creation date': int(time.time()),  # Current timestamp
    }

    # Bencode the data
    bencoded_data = bencodepy.encode(torrent_info)

    # Write to torrent file
    with open(filename.split('.')[0] + '.torrent', 'wb') as torrent_file:
        torrent_file.write(bencoded_data)

    
#filename = input('Enter filename: ')
# Example usage
#create_torrent_file(filename, 256)
