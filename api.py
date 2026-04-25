from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from blockchain import Blockchain, Wallet
from fastapi.middleware.cors import CORSMiddleware
import hashlib

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blockchain
blockchain = Blockchain()

# =========================
# USERS
# =========================
users = {}

class UserRequest(BaseModel):
    username: str
    password: str

class TxUserRequest(BaseModel):
    from_user: str
    to_user: str
    amount: float


# -----------------------
# REGISTER
# -----------------------
@app.post("/register")
def register(user: UserRequest):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    password_hash = hashlib.sha256(user.password.encode()).hexdigest()

    wallet = Wallet()
    blockchain.create_genesis_funds(wallet.get_address(), 100)

    users[user.username] = {
        "password": password_hash,
        "wallet": wallet
    }

    return {
        "message": "Usuário criado",
        "address": wallet.get_address()
    }


# -----------------------
# LOGIN
# -----------------------
@app.post("/login")
def login(user: UserRequest):
    if user.username not in users:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    password_hash = hashlib.sha256(user.password.encode()).hexdigest()

    if users[user.username]["password"] != password_hash:
        raise HTTPException(status_code=401, detail="Senha inválida")

    return {"message": "Login OK"}


# -----------------------
# BALANCE
# -----------------------
@app.get("/balance/{username}")
def get_balance(username: str):
    if username not in users:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    wallet = users[username]["wallet"]
    balance = blockchain.get_balance(wallet.get_address())

    return {"balance": balance}


# -----------------------
# SEND (USER)
# -----------------------
@app.post("/send")
def send(req: TxUserRequest):
    if req.from_user not in users or req.to_user not in users:
        raise HTTPException(status_code=404, detail="Usuário inválido")

    sender = users[req.from_user]["wallet"]
    receiver = users[req.to_user]["wallet"]

    tx = blockchain.create_transaction(
        sender,
        receiver.get_address(),
        req.amount
    )

    blockchain.add_transaction(tx)

    return {"message": "Transação criada"}


# =========================
# MODO ANTIGO (ÍNDICE)
# =========================
wallets = []

class TxRequest(BaseModel):
    from_index: int
    to_index: int
    amount: float


@app.post("/wallet")
def create_wallet():
    wallet = Wallet()
    wallets.append(wallet)

    blockchain.create_genesis_funds(wallet.get_address(), 100)

    return {"address": wallet.get_address()}


@app.get("/wallets")
def get_wallets():
    result = []
    for w in wallets:
        result.append({
            "address": w.get_address(),
            "balance": blockchain.get_balance(w.get_address())
        })
    return result


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


@app.post("/mine")
def mine():
    blockchain.mine_pending_transactions()
    return {"msg": "Bloco minerado"}


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