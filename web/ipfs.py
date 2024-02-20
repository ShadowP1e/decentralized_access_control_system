import requests
from dotenv import load_dotenv
import os

load_dotenv()

PYNATA_API_KEY = os.getenv('PYNATA_API_KEY')


def upload_file_to_ipfs(file):
    url = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
    headers = {'Authorization': f'Bearer {PYNATA_API_KEY}'}

    response = requests.post(url, files={'file': file}, headers=headers)
    return response.json()['IpfsHash']


def delete_file_in_ipfs(cid):
    url = "https://api.pinata.cloud/pinning/unpin/" + cid
    headers = {'Authorization': f'Bearer {PYNATA_API_KEY}'}

    response = requests.delete(url, headers=headers)
    return response.json()


def get_file_list_from_ipfs():
    url = 'https://api.pinata.cloud/data/pinList?status=pinned'
    headers = {'Authorization': f'Bearer {PYNATA_API_KEY}'}

    response = requests.get(url, headers=headers)
    return response.json()


def get_file_from_ipfs(file_hash):
    url = 'https://ipfs.io/ipfs/' + file_hash
    response = requests.get(url)
    return response.content
