import json
from final import hash_to_128_bits,hash_to_prime

file_path = 'C:/Users/Aksha/rsa/witness.json'
file_path_1 = 'C:/Users/Aksha/rsa/hashes.json'

with open(file_path, 'r') as file:
    witness_data = json.load(file)

with open(file_path_1, 'r') as file:
    hash_data = json.load(file)

def number_to_padded_hex(number):
    hex_str = hex(number)[2:]

    padded_hex_str = hex_str.zfill(64)
    
    return '0x' + padded_hex_str

def get_value(pair_key):
    witness = witness_data.get(pair_key, "Key not found") , hash_to_prime(pair_key)
    exponent = hash_data.get(pair_key, "Key not found") , hash_to_prime(pair_key)

    return witness ,exponent

input = input("Enter a string: ")
witness , exponent = get_value(input)
print("witness",hex(witness[0]))
print("exponent",number_to_padded_hex(exponent[0]))