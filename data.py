from web3 import Web3


# Connect to Infura
infura_url = 'https://mainnet.infura.io/v3/4949d498183947b9915ffa888117be42'
web3 = Web3(Web3.HTTPProvider(infura_url))

block_number = 10255489  # Replace with the block number you're interested in

# Get block details
block = web3.eth.get_block(block_number, full_transactions=True)

transaction_hashes = []
transaction_receipts = []


def main() : 
 for tx in block.transactions:
    transaction_hashes.append(tx.hash.hex())
    transaction_receipts.append(web3.eth.get_transaction_receipt(tx.hash))
 return transaction_hashes     


# print(transaction_receipts[0])
print(transaction_hashes)