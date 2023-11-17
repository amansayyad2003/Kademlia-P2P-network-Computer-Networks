

import hashlib
import bencodepy
import time

def decode_torrent_file(torrent_file_path):
    with open(torrent_file_path, 'rb') as file:
        torrent_data = bencodepy.decode(file.read())

    info = torrent_data[b'info']
    print(f"File Name: {info[b'name'].decode('utf-8')}")
    print(f"File Size: {info[b'length']} bytes")
    print(f"Piece Length: {info[b'piece length']} bytes")

    # Extract and display the MD5 checksum
    md5sum = info.get(b'md5sum', 'Not Available')
    print(f"MD5 Checksum: {md5sum}")

    # Extract and display the concatenated SHA-1 hashes of all pieces
    concatenated_hashes = info[b'pieces']
    print("\nConcatenated SHA-1 Hashes of All Pieces:")
    print(concatenated_hashes.hex())

    # Split the concatenated SHA-1 values using the specified separator ('/')
    piece_hashes = [concatenated_hashes[i:i+20].hex() for i in range(0, len(concatenated_hashes), 21)]

    # Display the piece number and corresponding SHA-1 value
    print("\nPiece Numbers and Corresponding SHA-1 Hashes:")
    for i, hash_value in enumerate(piece_hashes):
        print(f"Piece {i + 1}: {hash_value}")

    # Display additional information
    print(f"\nCreated By: {torrent_data.get(b'created by', 'Unknown')}")
    creation_date = torrent_data.get(b'creation date')
    print(f"Creation Date: {time.ctime(creation_date) if creation_date else 'Unknown'}")

    retrieved_info = {
        'file-name': info[b'name'].decode('utf-8'),
        'file-size': info[b'length'],
        'piece-length': info[b'piece length'],
        'md5sum': md5sum,
        'piece-hashes': piece_hashes,
        'created-by': torrent_data.get(b'created by', 'Unknown'),
        'creation-date': time.ctime(creation_date) if creation_date else 'Unknown'
    }

    return retrieved_info

