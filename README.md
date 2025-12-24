# Build-From-Scratch---Season-I_OldGuard
OldGuard is a blockchain node built without libraries. It implements the SHA-256 Sigma compression functions manually via bitwise operators and handles HTTP traffic through raw TCP sockets. Includes a custom Proof-of-Work algorithm and a reputation logic system that autonomously bans malicious actors.

# OldGuard: The Immutable Reputation Ledger

> "Old money lasts forever. OldGuard ensures it. We use an immutable reputation ledger to make your history permanent as stone but fast as lightning. We guard your legacy."

## What I Built
OldGuard is a "Zero-Dependency" blockchain node built entirely from scratch in Python. It features:

**Custom Cryptography:** A manual implementation of the SHA-256 standard (including Sigma compression functions).

**Reputation Consensus:** A protocol that tracks user behavior and automatically bans malicious actors.

**Raw Socket Server:** A custom HTTP server operating at the TCP transport layer, bypassing frameworks like Flask.


## How It Works Internally

### 1. The Engine (Manual SHA-256)
Instead of importing `hashlib`, I implemented the math directly. The core of the security relies on the **Sigma ($\Sigma$) Compression Functions**, which create the "Avalanche Effect" essential for immutability.
To make this work in Python (which has infinite integer precision), I engineered a helper function to simulate 32-bit hardware registers:
```python
def right_rotate(value, amount):
    # Enforces 32-bit boundary using the mask 0xFFFFFFFF
    return ((value >> amount) | (value << (32 - amount))) & 0xFFFFFFFF
```

### 2. The Network (Raw TCP)
The server does not use http.server. It listens on a raw TCP socket, intercepts byte streams, and manually parses HTTP headers by splitting strings on \r\n. It constructs raw HTTP byte streams for responses, giving us full control over the network packet structure.

### 3. The Reputation Logic
The ReputationChain class maintains a ledger of trust.
•	Positive Behavior: Successful transactions increase a user's score.
•	Negative Behavior: Fraudulent attempts decrease the score.
•	Ban Threshold: If a score drops below -1, the protocol automatically rejects their future blocks.

## Architecture
The system follows a strict Object-Oriented design:
•	ReputationChain: The manager that holds the list of blocks and enforces rules.
•	Block: The container that links to the previous hash and holds data.
•	Transaction: The payload (Sender, Receiver, Amount).
•	SHA256_Utility: The static engine that powers the mining proof-of-work.

# Flow of a Request:
1.	Client sends raw HTTP string ->
2.	Socket Listener intercepts bytes ->
3.	Manual Router parses POST /mine ->
4.	Consensus Engine verifies Reputation ->
5.	SHA-256 Engine performs Proof-of-Work ->
6.	Ledger updates & Server returns JSON.

# Steps to Run
Prerequisites
•	Python 3.x installed.
•	No external libraries required (Standard Library only).

# Running the Node
1. Copy path of OldGuard folder.
2. Open your termainl.
3. type in cd then past the copied path.
4. Press enter and run the server:

Bash
python server.py

• You should see: RAW SOCKET SERVER listening on port 8000...

Interacting with the Node.
1. Copy the localhost address and paste in your browser.
2. Enter the persons to be involved in the transactions, include postive and negitive values to see it in action.
