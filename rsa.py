from data import main
from final import setup, batch_add, create_all_membership_witnesses,verify_membership
import secrets , json

n, A0, S = setup()

transaction_hashes = main()

def ensure_even_length_hex(hex_str):
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return '0x' + hex_str


x_values = [hash[2:] if hash.startswith('0x') else hash for hash in transaction_hashes]

print("n",hex(n))
print("A0",A0)
print("S",S)

print("x:",x_values)
A1, Map = batch_add(A0,S,x_values,n)
print("A1",A1)
print("A1_hex",ensure_even_length_hex(hex(A1)))
witness, map = create_all_membership_witnesses(A0,S,n)


with open('witness.json', 'w') as f:
    json.dump(map, f, indent=4, default=str) 

with open('hashes.json', 'w') as f:
    json.dump(Map, f, indent=4, default=str) 

for i in range(len(x_values)) : 
 result,hash = verify_membership(A1,x_values[i],0,witness[i],n)
 print(result,hash)






