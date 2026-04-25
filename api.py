from fastapi import FastAPI
from pydantic import BaseModel
from blockchain import Blockchain, Wallet
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois a gente restringe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = Blockchain()
wallets = []

# -----------------------
# MODELO DE REQUISIÇÃO
# -----------------------
class TxRequest(BaseModel):
    from_index: int
    to_index: int
    amount: float


# -----------------------
# CRIAR CARTEIRA
# -----------------------
@app.post("/wallet")
def create_wallet():
    wallet = Wallet()
    wallets.append(wallet)

    blockchain.create_genesis_funds(wallet.get_address(), 100)

    return {"address": wallet.get_address()}


# -----------------------
# LISTAR CARTEIRAS
# -----------------------
@app.get("/wallets")
def get_wallets():
    result = []
    for w in wallets:
        result.append({
            "address": w.get_address(),
            "balance": blockchain.get_balance(w.get_address())
        })
    return result


# -----------------------
# TRANSAÇÃO
# -----------------------
@app.post("/transaction")
def send_transaction(req: TxRequest):
    sender = wallets[req.from_index]
    receiver = wallets[req.to_index]

    tx = blockchain.create_transaction(
        sender,
        receiver.get_address(),
        req.amount
    )

    blockchain.add_transaction(tx)

    return {"msg": "Transação criada"}


# -----------------------
# MINERAR
# -----------------------
@app.post("/mine")
def mine():
    blockchain.mine_pending_transactions()
    return {"msg": "Bloco minerado"}


# -----------------------
# VER BLOCKCHAIN
# -----------------------
@app.get("/chain")
def get_chain():
    return [
        {
            "index": b.index,
            "hash": b.hash,
            "prev": b.previous_hash,
            "txs": [tx.to_dict() for tx in b.transactions]
        }
        for b in blockchain.chain
    ]