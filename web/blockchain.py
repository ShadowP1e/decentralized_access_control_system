import json
from eth_typing import ChecksumAddress, HexAddress, HexStr
from web3 import Web3

from ipfs import upload_file_to_ipfs

GAS_LIMIT = 6721975
GAS_PRICE = 20000000000


def format_error(error):
    return error.split(':')[1]


class AuthContract:
    def __init__(self, contract, account_address, w3):
        self.contract = contract
        self.account_address = account_address
        self.w3 = w3

    def get_roles(self):
        return self.contract.functions.getRoles().call()

    def get_user_role(self, addr):
        return self.contract.functions.getUserRole(addr).call()

    def set_user_role(self, addr, role):
        tx_hash = self.contract.functions.setUserRole(addr, role).transact(
            {'from': self.account_address, 'gas': GAS_LIMIT, 'gasPrice': GAS_PRICE}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt


class StorageContract:
    def __init__(self, contract, account_address, w3):
        self.contract = contract
        self.account_address = account_address
        self.w3 = w3

    def create_directory(self, title):
        tx_hash = self.contract.functions.createDirectory(title).transact(
            {'from': self.account_address, 'gas': GAS_LIMIT, 'gasPrice': GAS_PRICE}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def delete_directory(self, title):
        tx_hash = self.contract.functions.deleteDirectory(title).transact(
            {'from': self.account_address, 'gas': GAS_LIMIT, 'gasPrice': GAS_PRICE}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def get_directory(self, title):
        return self.contract.functions.getDirectory(title).call()

    def get_directories(self):
        return self.contract.functions.getDirectories().call()

    def create_file(self, title, file_hash, directory, roles):
        tx_hash = self.contract.functions.createFile(title, file_hash, directory, roles).transact(
            {'from': self.account_address, 'gas': GAS_LIMIT, 'gasPrice': GAS_PRICE}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def delete_file(self, title, directory):
        tx_hash = self.contract.functions.deleteFile(title, directory).transact(
            {'from': self.account_address, 'gas': GAS_LIMIT, 'gasPrice': GAS_PRICE}
        )
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def get_file_hash(self, title, directory):
        return self.contract.functions.getFileHash(title, directory).call()


class User:
    def __init__(self, w3, private_key, auth_address, storage_address):
        self.account_address = w3.eth.account.from_key(private_key).address
        w3.eth.default_account = self.account_address

        with open('../contracts/AuthContract.json') as file:
            auth_contract_json = json.loads(file.read())
            auth_abi = auth_contract_json['abi']

        self.auth_contract = AuthContract(w3.eth.contract(address=auth_address, abi=auth_abi), self.account_address, w3)

        with open('../contracts/StorageContract.json') as file:
            storage_contract_json = json.loads(file.read())
            storage_abi = storage_contract_json['abi']

        self.storage_contract = StorageContract(w3.eth.contract(address=storage_address, abi=storage_abi),
                                                self.account_address, w3)

    def get_roles(self):
        return self.auth_contract.get_roles()

    def get_user_role(self, addr):
        return self.auth_contract.get_user_role(addr)

    def get_my_role(self):
        return self.auth_contract.get_user_role(self.account_address)

    def set_user_role(self, addr, role):
        self.auth_contract.set_user_role(addr, role)

    def create_directory(self, title):
        self.storage_contract.create_directory(title)

    def delete_directory(self, title):
        return self.storage_contract.delete_directory(title)

    def get_directory(self, title):
        return self.storage_contract.get_directory(title)

    def get_directories(self):
        return self.storage_contract.get_directories()

    def create_file(self, title, directory, file, roles):
        file_hash = upload_file_to_ipfs(file)
        self.storage_contract.create_file(title, file_hash, directory, roles)

    def delete_file(self, title, directory):
        self.storage_contract.delete_file(title, directory)

    def get_file_hash(self, title, directory):
        return self.storage_contract.get_file_hash(title, directory)


def string_address_to_checksum_address(address: str) -> ChecksumAddress:
    return ChecksumAddress(HexAddress(HexStr(address)))
