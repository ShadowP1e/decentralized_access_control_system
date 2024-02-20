from web3 import Web3


url = 'https://ethereum-sepolia.publicnode.com'

web3 = Web3(Web3.HTTPProvider(url))

print(web3.client_version)

block_number = web3.eth.block_number
print("Latest Block Number:", block_number)
