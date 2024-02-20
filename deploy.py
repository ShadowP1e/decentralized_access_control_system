from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))

private_key = '0xff25baa54705768881d1b661a7b34851df0a7e761b02dc4465e945544590a85d'
account_address = w3.eth.account.from_key(private_key).address
w3.eth.default_account = account_address

# Solidity contract source code
with open('contracts/AuthContract.json') as file:
    auth_contract_json = json.loads(file.read())

with open('contracts/StorageContract.json') as file:
    storage_contract_json = json.loads(file.read())


# Deploy the contracts
def deploy_contract(w3, contract_json, *args):
    bytecode = contract_json['bytecode']['object']
    abi = contract_json['abi']
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = Contract.constructor(*args).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    return contract_address


auth_contract_address = deploy_contract(w3, auth_contract_json, ["admin", "manager", "analyzer"])
storage_contract_address = deploy_contract(w3, storage_contract_json, auth_contract_address)

print("AuthContract deployed at:", auth_contract_address)
print("StorageContract deployed at:", storage_contract_address)
