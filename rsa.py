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

#  //1 




# import secrets
# import json
# from data import main
# from final import setup, batch_add, create_all_membership_witnesses, verify_membership, hash_to_prime, ACCUMULATED_PRIME_SIZE

# # Setup
# n, A0, S = setup()

# # Retrieve transaction hashes
# transaction_hashes = main()

# def ensure_even_length_hex(hex_str):
#     if hex_str.startswith("0x"):
#         hex_str = hex_str[2:]
#     if len(hex_str) % 2 != 0:
#         hex_str = '0' + hex_str
#     return '0x' + hex_str

# # Clean transaction hashes
# x_values = [hash[2:] if hash.startswith('0x') else hash for hash in transaction_hashes]

# # Display initial setup values
# print("n", hex(n))
# print("A0", A0)
# print("S", S)
# print("x:", x_values)

# # Batch add elements
# A1, Map = batch_add(A0, S, x_values, n)
# print("A1", A1)
# print("A1_hex", ensure_even_length_hex(hex(A1)))

# # Create membership witnesses
# witness, map = create_all_membership_witnesses(A0, S, n)

# # Save witnesses and hashes to files
# with open('witness.json', 'w') as f:
#     json.dump(map, f, indent=4, default=str)

# with open('hashes.json', 'w') as f:
#     json.dump(Map, f, indent=4, default=str)

# # Verify membership for each value
# for i in range(len(x_values)):
#     result, hash = verify_membership(A1, x_values[i], 0, witness[i], n)
#     print(result, hash)

# # Delete function
# def delete(A0, A, S, x, n):
#     if x not in S.keys():
#         return A
#     else:
#         del S[x]
#         product = 1
#         for element in S.keys():
#             nonce = S[element]
#             product *= hash_to_prime(element, ACCUMULATED_PRIME_SIZE, nonce)[0]
#         Anew = pow(A0, product, n)
#         return Anew

# # Batch delete function
# def batch_delete(A0, S, x_list, n):
#     for x in x_list:
#         del S[x]

#     if len(S) == 0:
#         return A0

#     return batch_add(A0, S, x_list, n)

# # Example usage of delete and batch_delete functions
# # Deleting a single element
# element_to_delete = x_values[0]
# A_new = delete(A0, A1, S, element_to_delete, n)
# print("A_new after delete:", A_new)

# # Batch deleting elements
# elements_to_delete = x_values[:2]
# A_new_batch = batch_delete(A0, S, elements_to_delete, n)
# print("A_new after batch delete:", A_new_batch)
