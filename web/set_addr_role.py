import os

from dotenv import load_dotenv
from web3 import Web3
from blockchain import User

load_dotenv()


def main():
    ganache_url = 'http://127.0.0.1:7545'
    web3 = Web3(Web3.HTTPProvider(ganache_url))

    private_key = '0xff25baa54705768881d1b661a7b34851df0a7e761b02dc4465e945544590a85d'

    auth_contract = os.getenv('AUTH_CONTRACT_ADDR')
    storage_contract = os.getenv('STORAGE_CONTRACT_ADDR')

    user = User(web3, private_key, auth_contract, storage_contract)
    addr = input('Address:')
    role = input('Role:')
    user.set_user_role(addr, role)
    print(user.get_user_role(addr))


if __name__ == '__main__':
    main()
