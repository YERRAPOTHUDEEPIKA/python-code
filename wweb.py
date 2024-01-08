from flask import Flask, request, jsonify, render_template
from web3 import Web3
from eth_account import Account
import datetime

app = Flask(__name__)

infura_url = 'https://mainnet.infura.io/v3/322e82f085ff439f9b01313f409e8e67'
web3 = Web3(Web3.HTTPProvider(infura_url))
local_node_url = 'http://localhost:3000/'

class CryptoWebWallet:
    def __init__(self):
        self.users = []
        self.current_user = None
        self.balance = 0.0
        self.recipient = ""
        self.amount = 0.0
        self.transaction_history = []

    def generate_wallet(self):
        wallet = Account.create()
        wallet_address = wallet.address
        user = {
            'id': len(self.users) + 1,
            'address': wallet_address,
            'balance': 1000.0,
            'transaction_history': []
        }
        self.users.append(user)
        self.current_user = user

    def send_transaction(self):
        if self.balance >= self.amount:
            new_transaction = {
                'from': self.current_user['address'],
                'to': self.recipient,
                'amount': self.amount,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.current_user['transaction_history'].append(new_transaction)
            self.balance -= self.amount
            self.transaction_history.append(new_transaction)

crypto_wallet = CryptoWebWallet()

@app.route('/generate_wallet', methods=['POST'])
def generate_wallet_route():
    crypto_wallet.generate_wallet()
    return jsonify({'message': 'Wallet generated successfully'})

@app.route('/send_transaction', methods=['POST'])
def send_transaction_route():
    crypto_wallet.amount = float(request.json['amount'])
    crypto_wallet.recipient = request.json['recipient']
    crypto_wallet.send_transaction()
    return jsonify({'message': 'Transaction sent successfully'})

@app.route('/')
def index():
    return render_template('web.html')

if __name__ == '__main__':
    app.run(debug=True)
