import socket
import json
import os
import mimetypes
import sys

# Try to import your logic
try:
    from main import ReputationChain, Transaction, Block
except ImportError:
    print("CRITICAL ERROR: Could not import 'main.py'.")
    sys.exit(1)

# Initialize Network
network = ReputationChain()
HOST = '127.0.0.1'
PORT = 8000

def handle_request(raw_request):
    """
    Manually parses the HTTP request string.
    Example Input: 'GET /api/chain HTTP/1.1 ...'
    """
    try:
        # 1. Parse Headers
        request_str = raw_request.decode('utf-8')
        lines = request_str.split('\r\n')
        request_line = lines[0] # e.g. "GET /api/chain HTTP/1.1"
        
        # Break down the request line
        method, path, _ = request_line.split(' ')
        
        print(f"Incoming: {method} {path}")

        # --- ROUTE 1: GET API DATA ---
        if method == 'GET' and path == '/api/chain':
            chain_data = []
            for block in network.chain:
                chain_data.append({
                    "index": block.index,
                    "sender": block.transaction.sender,
                    "receiver": block.transaction.receiver,
                    "amount": block.transaction.amount,
                    "hash": block.hash,
                    "nonce": block.nonce
                })
            scores = network.get_current_scores()
            response_body = json.dumps({"chain": chain_data, "scores": scores, "difficulty": network.difficulty})
            return construct_response(200, response_body, 'application/json')

        # --- ROUTE 2: POST MINING REQUEST ---
        elif method == 'POST' and path == '/api/mine':
            # Extract the body (JSON) from the bottom of the request
            # HTTP headers and body are separated by a blank line (\r\n\r\n)
            try:
                body_parts = request_str.split('\r\n\r\n')
                if len(body_parts) > 1:
                    json_str = body_parts[1]
                    # Sometimes browsers send null bytes or extra whitespace
                    json_str = json_str.strip().rstrip('\x00') 
                    
                    data = json.loads(json_str)
                    sender = data['sender']
                    receiver = data['receiver']
                    amount = int(data['amount'])

                    # Logic
                    scores = network.get_current_scores()
                    if sender in scores and scores[sender] < network.BAN_THRESHOLD:
                         return construct_response(403, json.dumps({"error": "User Blacklisted"}), 'application/json')

                    previous = network.chain[-1]
                    new_txn = Transaction(sender, receiver, amount)
                    new_block = Block(previous.index + 1, new_txn, previous.hash)
                    
                    print(f"⛏️  Mining for {sender}...")
                    new_block.mine_block(network.difficulty)
                    network.chain.append(new_block)
                    
                    return construct_response(200, json.dumps({"message": "Mined"}), 'application/json')
            except Exception as e:
                print(f"Mining Error: {e}")
                return construct_response(500, json.dumps({"error": str(e)}), 'application/json')

        # --- ROUTE 3: STATIC FILES (HTML/CSS/JS) ---
        else:
            filename = path.strip("/")
            if filename == "": filename = "index.html"
            
            if os.path.exists(filename):
                mime_type, _ = mimetypes.guess_type(filename)
                with open(filename, 'rb') as f:
                    file_content = f.read()
                # We need a special helper for binary data (images/favicons) vs text
                return construct_bytes_response(200, file_content, mime_type or 'text/html')
            else:
                return construct_response(404, "404 Not Found", "text/plain")

    except Exception as e:
        print(f"Request Parsing Error: {e}")
        return construct_response(500, "Internal Server Error", "text/plain")

def construct_response(status_code, body, content_type):
    """
    Manually builds the HTTP response string.
    """
    response = f"HTTP/1.1 {status_code} OK\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += "Access-Control-Allow-Origin: *\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    response += "\r\n"
    response += body
    return response.encode('utf-8')

def construct_bytes_response(status_code, body_bytes, content_type):
    """
    Manually builds a response for binary files (required for stability).
    """
    header = f"HTTP/1.1 {status_code} OK\r\n"
    header += f"Content-Type: {content_type}\r\n"
    header += f"Content-Length: {len(body_bytes)}\r\n"
    header += "\r\n"
    return header.encode('utf-8') + body_bytes

# --- MAIN SERVER LOOP ---
def start_server():
    print(f"--- RAW SOCKET SERVER LISTENING ON {PORT} ---")
    print(f"Go to http://localhost:{PORT}")
    
    # Create a raw TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow port reuse (prevents "Address already in use" errors)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5) # Backlog of 5 connections

        while True:
            # Accept new connection
            client_socket, addr = server_socket.accept()
            
            # Receive raw bytes (up to 4096)
            request_data = client_socket.recv(4096)
            
            if request_data:
                # Handle request and get response bytes
                response_data = handle_request(request_data)
                # Send back the raw bytes
                client_socket.sendall(response_data)
            
            # Close the connection (HTTP is stateless)
            client_socket.close()

    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Server Crash: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()