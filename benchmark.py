import secrets, hashlib,random,time

RSA_KEY_SIZE = 3072  # RSA key size for 128 bits of security (modulu size)
RSA_PRIME_SIZE = int(RSA_KEY_SIZE / 2)
ACCUMULATED_PRIME_SIZE = 128  # taken from: LLX, "Universal accumulators with efficient nonmembership proofs", construction 1


def setup():
    p, q = generate_two_large_distinct_primes(RSA_PRIME_SIZE)
    n = p*q
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



def rabin_miller(num):
    # Returns True if num is a prime number.

    s = num - 1
    t = 0
    while s % 2 == 0:
        # keep halving s while it is even (and use t
        # to count how many times we halve s)
        s = s // 2
        t += 1

    for trials in range(5): # try to falsify num's primality 5 times
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1: # this test does not apply if v is 1.
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % num
    return True

def generate_large_prime(num_of_bits):
    while True:
        num = secrets.randbelow(pow(2, num_of_bits))
        if is_prime(num):
            return num


def generate_two_large_distinct_primes(num_of_bits):
    p = generate_large_prime(num_of_bits)
    while True:
        q = generate_large_prime(num_of_bits)
        while q != p:
            return p, q
        
def is_prime(num):
    # Return True if num is a prime number. This function does a quicker
    # prime number check before calling rabin_miller().

    if (num < 2):
        return False # 0, 1, and negative numbers are not prime

    # About 1/3 of the time we can quickly determine if num is not prime
    # by dividing by the first few dozen prime numbers. This is quicker
    # than rabin_miller(), but unlike rabin_miller() is not guaranteed to
    # prove that a number is prime.
    lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

    if num in lowPrimes:
        return True

    # See if any of the low prime numbers can divide num
    for prime in lowPrimes:
        if (num % prime == 0):
            return False

    # If all else fails, call rabin_miller() to determine if num is a prime.
    return rabin_miller(num)
    

def hash_to_prime(x, num_of_bits=128, nonce=0):
    num = hash_to_128_bits(x )
    while True:
        num = num + nonce 
        if is_prime(num):
            return num, nonce
        nonce = nonce + 1


def hash_to_128_bits(hex_string):
    # Convert the hexadecimal string to bytes
    hex_bytes = bytes.fromhex(hex_string)

    # Hash the bytes using SHA-256
    hash_result = hashlib.sha256(hex_bytes).digest()

    # Take the first 16 bytes (128 bits) of the hash result
    result_128_bits = int.from_bytes(hash_result[:16], byteorder='big')

    return result_128_bits


def verify_membership(A, x, nonce, proof, n):
    hash = hash_to_prime(x=x, num_of_bits=ACCUMULATED_PRIME_SIZE, nonce=nonce)[0]
    result = __verify_membership(A, hash, proof, n)
    return result , hash 
    

def __verify_membership(A, x, proof, n):
    return pow(proof, x, n) == A

def create_all_membership_witnesses(A0, S, n):
    # Generate the primes for each key in S
    primes = [hash_to_prime(x=x, nonce=0)[0] for x in S.keys()]
    # Compute the witnesses for the entire set of primes
    witnesses = root_factor(A0, primes, n)
    # Map each key in S to its corresponding witness
    membership_witnesses = {key: witnesses[i] for i, key in enumerate(S.keys())}
    return witnesses   ,membership_witnesses


def root_factor(g, primes, N):
    n = len(primes)
    if n == 1:
        return [g]

    n_tag = n // 2
    primes_L = primes[n_tag:n]
    product_L = calculate_product(primes_L)
    g_L = pow(g, product_L, N)

    primes_R = primes[0: n_tag]
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


n, A0, S = setup()

# print("n",n)
# print("A0",A0)
# print("S",S)

x_values = [secrets.token_hex(32) for _ in range(100000)]

A1_values = []

# print("x:",x_values)
# print("S",S)
start_time = time.time()
A1 = batch_add(A0,S,x_values,n)
end_time = time.time()
print(end_time - start_time)
print("A1",A1)

print("S",S)
witness = create_all_membership_witnesses(A0,S,n)
print("wintess:",witness)
print("n",n)

for i in range(2) : 
 result = verify_membership(A1,x_values[i],0,witness[i],n)
 print(result)
