import hashlib
import json
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1


# =========================
# WALLET
# =========================
class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def get_address(self):
        return self.public_key.to_string().hex()


# =========================
# UTXO STRUCTURES
# =========================
class TxInput:
    def __init__(self, tx_output_id):
        self.tx_output_id = tx_output_id


class TxOutput:
    def __init__(self, address, amount):
        self.address = address
        self.amount = amount


# =========================
# TRANSACTION
# =========================
class Transaction:
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.inputs = []
        self.outputs = []
        self.signature = None

    def calculate_hash(self):
        return hashlib.sha256(
            (str(self.from_address) + str(self.to_address) + str(self.amount)).encode()
        ).hexdigest()

    def sign_transaction(self, signing_key):
        if signing_key.get_verifying_key().to_string().hex() != self.from_address:
            raise Exception("Você não pode assinar transações de outra carteira!")

        tx_hash = self.calculate_hash()
        self.signature = signing_key.sign(tx_hash.encode()).hex()

    def is_valid(self):
        if self.from_address is None:
            return True

        if not self.signature:
            raise Exception("Transação sem assinatura!")

        public_key = VerifyingKey.from_string(
            bytes.fromhex(self.from_address), curve=SECP256k1
        )

        return public_key.verify(
            bytes.fromhex(self.signature),
            self.calculate_hash().encode()
        )

    # 🔥 SERIALIZAÇÃO CORRETA
    def to_dict(self):
        return {
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "inputs": [inp.tx_output_id for inp in self.inputs],
            "outputs": [
                {"address": out.address, "amount": out.amount}
                for out in self.outputs
            ],
            "signature": self.signature
        }


# =========================
# BLOCK
# =========================
class Block:
    def __init__(self, index, previous_hash, transactions, difficulty, timestamp=None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        print(f"⛏️ Minerando bloco {self.index}...")
        target = "0" * self.difficulty

        while True:
            hash_attempt = self.calculate_hash()
            if hash_attempt.startswith(target):
                print(f"✅ Bloco minerado: {hash_attempt}")
                return hash_attempt
            else:
                self.nonce += 1

    def has_valid_transactions(self):
        return all(tx.is_valid() for tx in self.transactions)


# =========================
# BLOCKCHAIN (UTXO)
# =========================
class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.utxos = {}

    def create_genesis_block(self):
        return Block(0, "0", [], self.difficulty)

    def get_latest_block(self):
        return self.chain[-1]

    # 🔥 saldo inicial (faucet)
    def create_genesis_funds(self, address, amount):
        self.utxos[f"genesis_{address}"] = TxOutput(address, amount)

    # 🔥 saldo real
    def get_balance(self, address):
        balance = 0
        for utxo in self.utxos.values():
            if utxo.address == address:
                balance += utxo.amount
        return balance

    # 🔥 cria transação com UTXO
    def create_transaction(self, sender_wallet, to_address, amount):
        sender_address = sender_wallet.get_address()

        if self.get_balance(sender_address) < amount:
            raise Exception("Saldo insuficiente!")

        total = 0
        used_utxos = []

        for utxo_id, utxo in self.utxos.items():
            if utxo.address == sender_address:
                total += utxo.amount
                used_utxos.append(utxo_id)
                if total >= amount:
                    break

        tx = Transaction(sender_address, to_address, amount)

        for utxo_id in used_utxos:
            tx.inputs.append(TxInput(utxo_id))

        tx.outputs.append(TxOutput(to_address, amount))

        if total > amount:
            tx.outputs.append(TxOutput(sender_address, total - amount))

        tx.sign_transaction(sender_wallet.private_key)

        return tx

    def add_transaction(self, transaction):
        if not transaction.from_address or not transaction.to_address:
            raise Exception("Transação deve ter origem e destino")

        if not transaction.is_valid():
            raise Exception("Transação inválida")

        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        block = Block(
            len(self.chain),
            self.get_latest_block().hash,
            self.pending_transactions,
            self.difficulty
        )

        self.chain.append(block)

        # 🔥 atualizar UTXOs
        for tx in self.pending_transactions:
            for tx_input in tx.inputs:
                if tx_input.tx_output_id in self.utxos:
                    del self.utxos[tx_input.tx_output_id]

            for idx, output in enumerate(tx.outputs):
                self.utxos[f"{tx.calculate_hash()}_{idx}"] = output

        self.pending_transactions = []
        self.save_chain()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if not current.has_valid_transactions():
                return False

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True
        
import os

def save_chain(self):
    data = []
    for block in self.chain:
        data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": [tx.to_dict() for tx in block.transactions],
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })

    with open("chain.json", "w") as f:
        json.dump(data, f, indent=4)
        
def load_chain(self):
    if not os.path.exists("chain.json"):
        return

    with open("chain.json", "r") as f:
        data = json.load(f)

    # (simples: só reusa os dados, sem reconstruir objetos completos ainda)
    print("🔄 Blockchain carregada do arquivo")