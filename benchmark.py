import secrets, hashlib, random, time

RSA_KEY_SIZE = 3072  
RSA_PRIME_SIZE = int(RSA_KEY_SIZE / 2)
ACCUMULATED_PRIME_SIZE = 128  


def setup():
    p, q = generate_two_large_distinct_primes(RSA_PRIME_SIZE)
    n = p * q
    A0 = secrets.randbelow(n)
    return n, A0, {}


def add(A, S, x, n):
    if x in S:
        return A
    else:
        hash_prime, nonce = hash_to_prime(x, ACCUMULATED_PRIME_SIZE)
        A = pow(A, hash_prime, n)
        S[x] = nonce
        return A


def batch_add(A_pre_add, S, x_list, n):
    product = 1
    Map = {}
    for x in x_list:
        if x not in S:
            hash_prime, nonce = hash_to_prime(x, ACCUMULATED_PRIME_SIZE)
            S[x] = nonce
            Map[x] = hash_prime
            product *= hash_prime
    A_post_add = pow(A_pre_add, product, n)
    return A_post_add, Map


def generate_large_prime(num_of_bits):
    while True:
        num = secrets.randbelow(pow(2, num_of_bits))
        if is_prime(num):
            return num


def generate_two_large_distinct_primes(num_of_bits):
    p = generate_large_prime(num_of_bits)
    while True:
        q = generate_large_prime(num_of_bits)
        if q != p:
            return p, q


def is_prime(num):
    if num < 2:
        return False
    if num % 2 == 0 and num > 2:
        return False
    for _ in range(10):  # Miller-Rabin test
        a = random.randint(2, num - 1)
        if pow(a, num - 1, num) != 1:
            return False
    return True


def hash_to_prime(x, num_of_bits=128, nonce=0):
    num = hash_to_128_bits(x)
    while True:
        num += nonce
        if is_prime(num):
            return num, nonce
        nonce += 1


def hash_to_128_bits(hex_string):
    hex_bytes = bytes.fromhex(hex_string)
    hash_result = hashlib.sha256(hex_bytes).digest()
    return int.from_bytes(hash_result[:16], byteorder='big')


def verify_membership(A, x, nonce, proof, n):
    hash_value = hash_to_prime(x, ACCUMULATED_PRIME_SIZE, nonce)[0]
    return pow(proof, hash_value, n) == A, hash_value


def create_all_membership_witnesses(A0, S, n):
    primes = [hash_to_prime(x, nonce=0)[0] for x in S.keys()]
    witnesses = root_factor(A0, primes, n)
    return {key: witnesses[i] for i, key in enumerate(S.keys())}


def root_factor(g, primes, N):
    n = len(primes)
    if n == 1:
        return [g]

    n_half = n // 2
    primes_L = primes[n_half:n]
    product_L = calculate_product(primes_L)
    g_L = pow(g, product_L, N)

    primes_R = primes[0:n_half]
    product_R = calculate_product(primes_R)
    g_R = pow(g, product_R, N)

    L = root_factor(g_L, primes_R, N)
    R = root_factor(g_R, primes_L, N)

    return L + R


def calculate_product(lst):
    r = 1
    for x in lst:
        r *= x
    return r


# **Setup RSA accumulator**
start_setup = time.time()
n, A0, S = setup()
end_setup = time.time()

# **Print RSA Parameters**
print(f"\n=== RSA ACCUMULATOR SETUP ===")
print(f"n (Modulus): {n}")
print(f"A0 (Initial Accumulator): {A0}")
print(f"Setup Time: {end_setup - start_setup:.5f} seconds\n")

# **Batch Addition**
x_values = [secrets.token_hex(32) for _ in range(10)]

start_add = time.time()
A1, _ = batch_add(A0, S, x_values, n)
end_add = time.time()

print(f"Batch addition time: {end_add - start_add:.5f} seconds")
print(f"Updated Accumulator (A1): {A1}\n")

# **Generate Membership Witnesses**
membership_witnesses = create_all_membership_witnesses(A0, S, n)

# **Verify Membership for Each Element**
print("=== MEMBERSHIP VERIFICATION ===")
for i, x in enumerate(x_values):
    proof = membership_witnesses.get(x)

    if proof is not None:
        result, hashed_x = verify_membership(A1, x, 0, proof, n)
        print(f"Element {i}: Verification = {result}, Hashed Value = {hashed_x}, Witness = {proof}")
    else:
        print(f"Element {i}: Witness not found, verification failed.")

print("\nExecution complete.")
