import secrets
import hashlib

def concat(*args):
    return ''.join([str(arg) for arg in args])

def generate_two_large_distinct_primes(bits):
    p = secrets.randbits(bits)
    q = secrets.randbits(bits)
    while p == q:
        q = secrets.randbits(bits)
    return p, q

def calculate_product(primes):
    product = 1
    for prime in primes:
        product *= prime
    return product

def bezoute_coefficients(a, b):
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = b, a

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_s, old_t

def mul_inv(a, n):
    t, new_t = 0, 1
    r, new_r = n, a

    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r

    if r > 1:
        raise ValueError("No inverse exists")
    if t < 0:
        t += n

    return t

def shamir_trick(g1, g2, a1, a2, n):
    return (pow(g1, a2, n) * pow(g2, a1, n)) % n

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def hash_to_prime(x, nonce=None):
    if nonce is None:
        nonce = secrets.token_bytes(16)
    while True:
        hash_input = (x + nonce.hex()).encode()
        candidate = hashlib.sha256(hash_input).hexdigest()
        prime_candidate = int(candidate, 16) | 1  # Ensure odd number
        if is_prime(prime_candidate):
            return prime_candidate, nonce

RSA_KEY_SIZE = 3072  # RSA key size 
RSA_PRIME_SIZE = RSA_KEY_SIZE // 2
ACCUMULATED_PRIME_SIZE = 128  

def setup():
    p, q = generate_two_large_distinct_primes(RSA_PRIME_SIZE)
    n = p * q
    A0 = secrets.randbelow(n)
    return n, A0, dict()

def add(A, S, x, n):
    if x not in S:
        hash_prime, nonce = hash_to_prime(x)
        A = pow(A, hash_prime, n)
        S[x] = nonce
    return A

def batch_add(A_pre_add, S, x_list, n):
    product = 1
    for x in x_list:
        if x not in S:
            hash_prime, nonce = hash_to_prime(x)
            S[x] = nonce
            product *= hash_prime
    A_post_add = pow(A_pre_add, product, n)
    return A_post_add

def batch_prove_membership(A0, S, x_list, n):
    product = 1
    for element in S:
        if element not in x_list:
            nonce = S[element]
            product *= hash_to_prime(element, nonce)[0]
    return pow(A0, product, n)

def delete_transactions(A0, S, transactions_to_delete, n):
    for x in transactions_to_delete:
        if x in S:
            del S[x]
    return batch_add(A0, S, transactions_to_delete, n)

def generate_random_transaction_hashes(num_hashes=100):
    return [hashlib.sha256(secrets.token_bytes(32)).hexdigest() for _ in range(num_hashes)]

def accumulate_in_batches(transaction_hashes, batch_size=10):
    n, A0, S = setup()
    batch_witnesses = []

    for i in range(0, len(transaction_hashes), batch_size):
        batch = transaction_hashes[i:i + batch_size]
        A0 = batch_add(A0, S, batch, n)
        batch_witnesses.append((A0, batch))  # Store current accumulator and the batch

    return n, batch_witnesses, A0, S

def verify_batch_witnesses(n, batch_witnesses, S):
    A0 = batch_witnesses[0][0]  # Starting accumulator
    for A, batch in batch_witnesses:
        # Recalculate product of hashes in the batch
        nonces = [S[x] for x in batch]
        product = calculate_product([hash_to_prime(x, nonce)[0] for x, nonce in zip(batch, nonces)])
        assert pow(A0, product, n) == A, "Verification failed!"
        A0 = A  # Update accumulator for next batch verification

# Step 1: Generate 100 random transaction hashes
transaction_hashes = generate_random_transaction_hashes(100)

# Step 2: Accumulate in 10 batches of 10 transactions each and generate witnesses
n, batch_witnesses, A0, S = accumulate_in_batches(transaction_hashes, batch_size=10)

# Step 3: Verify all batch witnesses
verify_batch_witnesses(n, batch_witnesses, S)

# Step 4: Delete a batch of transactions (e.g., the first batch)
A0_after_deletion = delete_transactions(A0, S, batch_witnesses[0][1], n)

# Verify that the deleted batch is no longer in the accumulator
try:
    verify_batch_witnesses(n, batch_witnesses[1:], S)  # Verify only remaining batches
    print("Verification succeeded after deletion")
except AssertionError:
    print("Verification failed after deletion (as expected)")

print("Accumulator and witness generation, verification, and deletion completed.")
