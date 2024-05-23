import secrets
import hashlib
import random
import time
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed
from sympy import nextprime

RSA_KEY_SIZE = 3072
RSA_PRIME_SIZE = int(RSA_KEY_SIZE / 2)
ACCUMULATED_PRIME_SIZE = 128

def setup():
    p, q = generate_two_large_distinct_primes(RSA_PRIME_SIZE)
    n = p * q
    A0 = secrets.randbelow(n)
    return n, A0, dict()

def add(A, S, x, n):
    if x in S.keys():
        return A
    else:
        hash_prime, nonce = hash_to_prime(x, ACCUMULATED_PRIME_SIZE)
        A = pow(A, hash_prime, n)
        S[x] = nonce
        return A

def batch_add(A_pre_add, S, x_list, n):
    def process_element(x):
        if x not in S:
            hash_prime, nonce = hash_to_prime(x, ACCUMULATED_PRIME_SIZE)
            return (x, hash_prime, nonce)
        return None

    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        futures = {executor.submit(process_element, x): x for x in x_list}

        product = 1
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                x, hash_prime, nonce = result
                S[x] = nonce
                product *= hash_prime

    A_post_add = pow(A_pre_add, product, n)
    return A_post_add

def rabin_miller(num):
    s = num - 1
    t = 0
    while s % 2 == 0:
        s = s // 2
        t += 1

    for _ in range(5):
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                i += 1
                v = (v ** 2) % num
    return True

def generate_large_prime(num_of_bits):
    def generate_candidate():
        while True:
            num = secrets.randbelow(1 << num_of_bits)
            if is_prime(num):
                return num

    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        future = executor.submit(generate_candidate)
        return future.result()

def generate_two_large_distinct_primes(num_of_bits):
    with ProcessPoolExecutor(max_workers=2) as executor:
        future_p = executor.submit(generate_large_prime, num_of_bits)
        future_q = executor.submit(generate_large_prime, num_of_bits)

        p = future_p.result()
        q = future_q.result()

        while p == q:
            q = generate_large_prime(num_of_bits)

        return p, q

def is_prime(num):
    if num < 2:
        return False

    low_primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
        71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
        151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
        233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
        317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
        419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
        503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601,
        607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
        701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809,
        811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907,
        911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
    ]

    if num in low_primes:
        return True

    for prime in low_primes:
        if num % prime == 0:
            return False

    return rabin_miller(num)

def hash_to_prime(x, num_of_bits=128, nonce=0):
    num = hash_to_128_bits(x)
    num += nonce
    prime = nextprime(num)
    return prime, nonce

def hash_to_128_bits(hex_string):
    hex_bytes = bytes.fromhex(hex_string)
    hash_result = hashlib.sha256(hex_bytes).digest()
    result_128_bits = int.from_bytes(hash_result[:16], byteorder='big')
    return result_128_bits

def verify_membership(A, x, nonce, proof, n):
    return __verify_membership(A, hash_to_prime(x=x, num_of_bits=ACCUMULATED_PRIME_SIZE, nonce=nonce)[0], proof, n)

def __verify_membership(A, x, proof, n):
    return pow(proof, x, n) == A

def create_all_membership_witnesses(A0, S, n):
    primes = [hash_to_prime(x=x, nonce=0)[0] for x in S.keys()]
    return root_factor(A0, primes, n)

def root_factor(g, primes, N):
    n = len(primes)
    if n == 1:
        return [g]

    n_tag = n // 2
    primes_L = primes[n_tag:n]
    product_L = calculate_product(primes_L)
    g_L = pow(g, product_L, N)

    primes_R = primes[0:n_tag]
    product_R = calculate_product(primes_R)
    g_R = pow(g, product_R, N)

    with ProcessPoolExecutor(max_workers=2) as executor:
        future_L = executor.submit(root_factor, g_L, primes_R, N)
        future_R = executor.submit(root_factor, g_R, primes_L, N)

        L = future_L.result()
        R = future_R.result()

    return L + R

def calculate_product(lst):
    r = 1
    for x in lst:
        r *= x
    return r

n, A0, S = setup()

x_values = [secrets.token_hex(32) for _ in range(100000)]

start_time = time.time()
A1 = batch_add(A0, S, x_values, n)
end_time = time.time()
print(end_time - start_time)
print("A1", A1)
