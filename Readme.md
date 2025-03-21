# RSA Accumulator Repository

This repository is maintained by Witness Chain . The project implements an RSA accumulator along with various functionalities for data extraction, benchmarking, and on-chain verification. The code is designed to be efficient, with support for multi-core processing and batching.

## Table of Contents
- [Overview](#overview)
- [Files and Descriptions](#files-and-descriptions)
- [Usage](#usage)
- [Contributing](#contributing)

## Overview
The RSA accumulator is a powerful cryptographic tool that allows for the succinct proof of membership or non-membership within a set of elements. This repository provides a robust implementation of the RSA accumulator, including additional scripts for data extraction, benchmarking, and integration with smart contracts for on-chain verification.

## Files and Descriptions

1. **allFunctions.py**
   - Contains the basic boilerplate of all functions used in the RSA accumulator.
   - This file includes utility functions that are essential for the operation of the accumulator and are reused across multiple scripts.

2. **data.py**
   - Extracts transaction data from a range of blockchain nodes using the Infura API.
   - This script serves as the data retrieval backbone, ensuring that transaction data is readily available for the RSA processes.

3. **benchmark.py**
   - Generates 100,000 random hashes to benchmark various aspects of the RSA accumulator.
   - The benchmarking focuses on measuring accumulation time, witness generation time, and verification time to evaluate performance.

4. **rsa.py**
   - The core script for performing RSA accumulator operations on the transaction data retrieved by `data.py`.
   - Handles the core RSA computations necessary for accumulating elements and generating proofs.

5. **rsa_with_delete.py**
   - Extends the functionality of `rsa.py` by adding the ability to delete elements from the RSA accumulator.
   - Useful for scenarios where elements need to be dynamically managed within the accumulator.

6. **verify.sol**
   - A Solidity contract designed for on-chain verification of RSA accumulator proofs.
   - Enables integration of RSA accumulator functionalities within blockchain environments, providing a means for decentralized verification.

7. **checkpoint.py**
   - Code to generate and store checkpoints of the accumulator's state.
   - Note: This script is still under development and has not yet been fully tested.

8. **multi.py** and **multi1.py**
   - Implement RSA accumulator operations utilizing multiple processing cores for improved performance.
   - These scripts parallelize the RSA computations, making the system more efficient on multi-core processors.

9. **witness.json**
   - Stores all witnesses generated by the `rsa.py` script.
   - Witnesses are used to prove the membership or non-membership of elements within the accumulator.

10. **transactions.json**
    - A storage file for all retrieved transactions and their corresponding hashes.
    - Acts as the local database for transaction data that is processed by the RSA accumulator.

11. **batchRsa.py**
    - Implements batching functionality to accumulate multiple elements in a single operation.
    - Note: This script is experimental and has not been fully tested yet.
   
## Usage

**Running RSA Operations:**

To perform RSA operations on transaction data, use the `rsa.py` script:

```bash
python rsa.py
```

**Benchmarking:**

To run benchmarks on hash generation, accumulation, and verification times, use the `benchmark.py` script:

```bash
python benchmark.py
```

**Multi-Core Processing (Experimental):**

Utilize multiple processing cores for RSA computations with:

```bash
python multi.py
```

**On-Chain Verification:**

1. **Compile the `verify.sol` contract:**

   You may need to compile the `verify.sol` contract using a Solidity compiler before deploying it on-chain. Here are two options:

   - **Solidity Compiler (solc):**

     - Install the Solidity compiler for your environment.
     - Use the `solc` command to compile the contract:

     ```bash
     solc --bin --abi verify.sol
     ```

     This will generate two files: `verify.sol.bin` and `verify.sol.abi`. You'll need these for deployment.

   - **Remix IDE:**

     - Open Remix IDE ([https://remix.ethereum.org](https://remix.ethereum.org)) and create a new project.
     - Paste the contents of `verify.sol` into the editor.
     - Select the compiler version and environment (e.g., Injected Web3).
     - Click the "Compile" button.
     - You can then access the compiled bytecode and ABI from the "Compile" tab.

2. **Deploy the Contract:**

   Deploy the compiled contract (bytecode) to your preferred blockchain using its deployment tools. The specific steps will vary depending on the blockchain you choose.

3. **Interact with the Contract:**

   Once deployed, interact with the contract's functions (using its ABI) to perform on-chain verification of RSA accumulator proofs. Refer to the blockchain's documentation and smart contract interaction tools for details.

**Contributing**

Contributions are welcome! Please fork the repository and submit a pull request with your improvements. Ensure that your code adheres to the repository's style guidelines.


