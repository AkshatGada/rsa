from data import main
from final import setup, batch_add, create_all_membership_witnesses,verify_membership

n, A0, S = setup()

transaction_hashes = main()


# Remove '0x' from each element
x_values = [hash[2:] if hash.startswith('0x') else hash for hash in transaction_hashes]

# Print the cleaned hashes
print("n",n)
print("A0",A0)
print("S",S)

A1_values = []

print("x:",x_values)
print("S",S)
A1 = batch_add(A0,S,x_values,n)
print("A1",A1)
print("S",S)
witness = create_all_membership_witnesses(A0,S,n)
print("wintess:",witness)
print("n",n)

for i in range(len(x_values)) : 
 result = verify_membership(A1,x_values[i],0,witness[i],n)
 print(result)