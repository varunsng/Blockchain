#Cryptocurrency

import datetime
import json
import hashlib
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        # contains list of transactions that are added before a bloack is created
        self.transactions = []
        # Genesis Block
        self.create_block(proof = 1,prev_hash = '0')
        self.nodes = set()

    def create_block(self,proof,prev_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': prev_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    # get last block in the chain
    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof+=1
        return new_proof
    
    # 2 methods to check that previous hash matches and that proof of work is correct
    
    def hash(self, block):
        
        # convert the entire block into a string
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2-prev_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index+=1
        return True
    
    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount})
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1
    
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            # find largest chain
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
# Mining Blockchain

# Create web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# Create blockchain
bc = Blockchain()

# create address for node on port 5000
node_address = str(uuid4()).replace('-', '')

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = bc.get_prev_block()
    prev_proof = prev_block['proof']
    proof = bc.proof_of_work(prev_proof)
    prev_hash = bc.hash(prev_block)
    bc.add_transaction(sender = node_address, receiver = "Varun", amount = 2)
    block = bc.create_block(proof, prev_hash)
    
    response = {'message': "You mined a block chain!",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200

# get full blockchain

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': bc.chain,
                'length': len(bc.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    if bc.is_chain_valid(bc.chain):
        response = {'Is_valid': 'Yes'}
    else:
        response = {'Is_valid': 'No'}
    return jsonify(response), 200



# adding new transaction to blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    # get json file from postman
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of transaction are missing', 400
    index = bc.add_transaction( sender = json['sender'], receiver = json['receiver'], amount = json['amount'])
    response = {'message': f'Transaction will be added {index}'}
    return jsonify(response), 201

# connect new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        bc.add_node(node)
    response = {'message': "All nodes connected. Blockchain now contains the following nodes",
                'total_nodes': list(bc.nodes)}
    return jsonify(response), 201

#replacing chain by longest chain
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    if bc.replace_chain():
        response = {'message': 'Chain replaced by longest chain',
                    'new_chain': bc.chain}
    else:
        response = {'message': 'Chain is the largest one',
                    'actual_chain': bc.chain}
    return jsonify(response), 200



# run app
app.run(host= '0.0.0.0',port=5001)
                                    
    