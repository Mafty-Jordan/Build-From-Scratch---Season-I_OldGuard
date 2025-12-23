# PART 1: THE ENGINE (SHA-256)

H_INIT = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
     0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
     0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
     0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
     0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
     0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

def right_rotate(value, amount):
    return ((value >> amount) | (value << (32 - amount))) & 0xFFFFFFFF

def sha256_custom(message):
    if isinstance(message, str): message = [ord(c) for c in message]
    original_length_bits = len(message) * 8
    message.append(0x80)
    while (len(message) % 64) != 56: message.append(0)
    for i in range(7, -1, -1): message.append((original_length_bits >> (i * 8)) & 0xFF)
    h = list(H_INIT)
    for i in range(0, len(message), 64):
        chunk = message[i:i + 64]
        w = [0] * 64
        for j in range(16): w[j] = (chunk[j * 4] << 24) | (chunk[j * 4 + 1] << 16) | (chunk[j * 4 + 2] << 8) | (chunk[j * 4 + 3])
        for j in range(16, 64):
            s0 = right_rotate(w[j - 15], 7) ^ right_rotate(w[j - 15], 18) ^ (w[j - 15] >> 3)
            s1 = right_rotate(w[j - 2], 17) ^ right_rotate(w[j - 2], 19) ^ (w[j - 2] >> 10)
            w[j] = (w[j - 16] + s0 + w[j - 7] + s1) & 0xFFFFFFFF
        a, b, c, d, e, f, g, h_var = h
        for j in range(64):
            S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h_var + S1 + ch + K[j] + w[j]) & 0xFFFFFFFF
            S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF
            h_var = g; g = f; f = e; e = (d + temp1) & 0xFFFFFFFF; d = c; c = b; b = a; a = (temp1 + temp2) & 0xFFFFFFFF
        h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, h_var])]
    result = ""
    for val in h: result += f"{val:08x}"
    return result

# PART 2: DATA STRUCTURES AND LOGIC

_tx_counter = 0

class Transaction:
    def __init__(self, sender, receiver, amount):
        global _tx_counter
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.id = _tx_counter
        _tx_counter += 1

    def to_string(self):
        return f"{self.sender}:{self.receiver}:{self.amount}:{self.id}"

class Block:
    def __init__(self, index, transaction, previous_hash):
        self.index = index
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = str(self.index) + self.transaction.to_string() + self.previous_hash + str(self.nonce)
        return sha256_custom(block_data)

    # Added basic mining function (without print statements/callbacks to keep it clean)
    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class ReputationChain:
    def __init__(self):
        # Genesis Block
        self.chain = [Block(0, Transaction("System", "System", 0), "0")]
        self.BAN_THRESHOLD = -1
        self.difficulty = 3 # Adjust this to make mining harder/easier

    def get_latest_block(self): 
        return self.chain[-1]

    def get_current_scores(self):
        scores = {}
        for i in range(1, len(self.chain)):
            txn = self.chain[i].transaction
            if txn.sender not in scores: scores[txn.sender] = 0
            if txn.receiver not in scores: scores[txn.receiver] = 0
            
            if txn.amount > 0:
                scores[txn.sender] += 1
                scores[txn.receiver] += 1
            else:
                scores[txn.sender] -= 5
        return scores

# This file is servers as the library.
# server.py will import ReputationChain from here.