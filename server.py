from flask import Flask, request, jsonify, render_template
from blockchain import Blockchain, Wallet

app = Flask(__name__)

blockchain = Blockchain()
wallets = []

# ------------------------
# HOME (interface web)
# ------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------
# CRIAR CARTEIRA
# ------------------------
@app.route("/wallet/create", methods=["POST"])
def create_wallet():
    wallet = Wallet()
    wallets.append(wallet)

    blockchain.create_genesis_funds(wallet.get_address(), 100)

    return jsonify({
        "address": wallet.get_address()
    })


# ------------------------
# LISTAR CARTEIRAS
# ------------------------
@app.route("/wallets", methods=["GET"])
def list_wallets():
    data = []

    for w in wallets:
        data.append({
            "address": w.get_address(),
            "balance": blockchain.get_balance(w.get_address())
        })

    return jsonify(data)


# ------------------------
# ENVIAR TRANSAÇÃO
# ------------------------
@app.route("/transaction", methods=["POST"])
def send_transaction():
    data = request.json

    sender = wallets[int(data["from"])]
    receiver = wallets[int(data["to"])]
    amount = float(data["amount"])

    tx = blockchain.create_transaction(sender, receiver.get_address(), amount)
    blockchain.add_transaction(tx)

    return jsonify({"message": "Transação criada"})


# ------------------------
# MINERAR
# ------------------------
@app.route("/mine", methods=["POST"])
def mine():
    blockchain.mine_pending_transactions()
    return jsonify({"message": "Bloco minerado"})


# ------------------------
# BLOCKCHAIN
# ------------------------
@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []

    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "hash": block.hash,
            "prev": block.previous_hash,
            "txs": [tx.to_dict() for tx in block.transactions]
        })

    return jsonify(chain_data)


if __name__ == "__main__":
    app.run(debug=True)