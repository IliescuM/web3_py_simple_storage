from matplotlib.image import NonUniformImage
from solcx import compile_standard, install_solc
import json
from web3 import Web3

with open("./simpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile our Solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"simpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode

bytecode = compiled_sol["contracts"]["simpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# get abi

abi = compiled_sol["contracts"]["simpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to rinkeby

w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/978ac736678e4021afda41985f819b09")
)
chain_id = 4
my_address = "0x82911E924eBf365Fc882fCb943fD9E6e9f667DE2"
private_key = "privatekey"

# create the contract in python
simpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

print(simpleStorage)

# get the latestest transaction

nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction

transaction = simpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

# Send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# Working with the contract, always need
# Contract address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change
# Initial value of favorite number
print(simple_storage.functions.retrive().call())
print("Updating Contract...")


store_transaction = simple_storage.functions.store(20).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
