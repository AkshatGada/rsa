from data import main
from final import setup, batch_add, create_all_membership_witnesses, verify_membership
import secrets
import json
import os

class CheckpointManager:
    def __init__(self, checkpoint_interval=10, checkpoint_dir='checkpoints'):
        self.checkpoint_interval = checkpoint_interval
        self.checkpoint_dir = checkpoint_dir
        self.batch_counter = 0

        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

    def save_checkpoint(self, batch_num, A, transactions):
        checkpoint_path = os.path.join(self.checkpoint_dir, f'checkpoint_{batch_num}.json')
        checkpoint_data = {
            'batch_num': batch_num,
            'A': A,
            'transactions': transactions
        }
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f, indent=4, default=str)

    def load_checkpoint(self, batch_num):
        checkpoint_path = os.path.join(self.checkpoint_dir, f'checkpoint_{batch_num}.json')
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        return checkpoint_data['A'], checkpoint_data['transactions']

    def should_save_checkpoint(self):
        self.batch_counter += 1
        return self.batch_counter % self.checkpoint_interval == 0

def ensure_even_length_hex(hex_str):
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return '0x' + hex_str

def reconstruct_witnesses(A, transactions, n):
    _, S, _ = setup()  # Reinitialize S
    A_reconstructed, _ = batch_add(A0, S, transactions, n)
    if A_reconstructed != A:
        raise ValueError("Reconstructed accumulator state does not match the saved state.")
    witnesses, _ = create_all_membership_witnesses(A0, S, n)
    return witnesses

n, A0, S = setup()

transaction_hashes = main()

x_values = [hash[2:] if hash.startswith('0x') else hash for hash in transaction_hashes]

print("n", hex(n))
print("A0", A0)
print("S", S)
print("x:", x_values)

checkpoint_manager = CheckpointManager(checkpoint_interval=10)

all_transactions = []
for i in range(0, len(x_values), 10):
    batch = x_values[i:i + 10]
    A1, Map = batch_add(A0, S, batch, n)
    all_transactions.extend(batch)
    A0 = A1  

    if checkpoint_manager.should_save_checkpoint():
        checkpoint_manager.save_checkpoint(checkpoint_manager.batch_counter, A0, all_transactions)
        print(f"Checkpoint saved for batch {checkpoint_manager.batch_counter}")

checkpoint_manager.save_checkpoint(checkpoint_manager.batch_counter, A0, all_transactions)

A_checkpoint, transactions_checkpoint = checkpoint_manager.load_checkpoint(checkpoint_manager.batch_counter)
witnesses = reconstruct_witnesses(A_checkpoint, transactions_checkpoint, n)

with open('witness.json', 'w') as f:
    json.dump(witnesses, f, indent=4, default=str)

with open('hashes.json', 'w') as f:
    json.dump(Map, f, indent=4, default=str)

for i in range(len(x_values)):
    result, hash = verify_membership(A1, x_values[i], 0, witnesses[i], n)
    print(result, hash)
