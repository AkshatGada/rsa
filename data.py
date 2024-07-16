from web3 import Web3 
import json

infura_url = 'https://mainnet.infura.io/v3/4949d498183947b9915ffa888117be42'
web3 = Web3(Web3.HTTPProvider(infura_url))

start_block = 10255489  
end_block = 10255490

n = end_block - start_block

all_transaction_hashes = []
all_transaction_receipts = []
map_transactions = {} 

def fetch_block_data(block_number):
    block = web3.eth.get_block(block_number,full_transactions=True)

    transaction_hashes = []
    transaction_receipts = []
    
    for tx in block.transactions:
        tx_hash = tx.hash.hex()
        tx_receipt = web3.eth.get_transaction_receipt(tx.hash)
        transaction_hashes.append(tx_hash)
        transaction_receipts.append(tx_receipt)
        map_transactions[tx_hash] = tx_receipt 

    return transaction_hashes , transaction_receipts

def main():
    for i in range(n):
        current_block_number = start_block + i
        hashes, receipts = fetch_block_data(current_block_number)
        all_transaction_hashes.extend(hashes)
        all_transaction_receipts.extend(receipts)

    return all_transaction_hashes

if __name__ == '__main__':
    transaction_hashes, transaction_receipts = main()

    with open('transactions.json', 'w') as f:
        json.dump(map_transactions, f, indent=4, default=str) 

