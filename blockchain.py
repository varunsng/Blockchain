#Blockchain

import datetime
import json
import hashlib
from flask import Flask, jsonify

class Blockchain:
    def __init__(self):
        self.chain = []
        
        # Genesis Block
        self.create_block(proof = 1,prev_hash = '0')

    def create_block(self,proof,prev_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': prev_hash}
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
    
    # 2 methods to check that previous hash matches and that prrof of work is correct
    
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
    
# Mining Blockchain

# Create web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# Create blockchain
bc = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = bc.get_prev_block()
    prev_proof = prev_block['proof']
    proof = bc.proof_of_work(prev_proof)
    prev_hash = bc.hash(prev_block)
    block = bc.create_block(proof, prev_hash)
    
    response = {'message': "You mined a block chain!",
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
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
# run app
app.run(host= '0.0.0.0',port=5000)
                                    
    