from dotenv import load_dotenv
import os
import requests
from moralis import evm_api
import json

load_dotenv()

api_key = os.getenv('API_KEY')

def wallet_pnl(address: str):
    params = {
        "chain": "eth",
        "address": address
    }
    result = evm_api.wallets.get_wallet_profitability_summary(
        api_key=api_key,
        params=params,
    )
    return result


def get_wallet_history(wallet: str, uid: int):
    params = {
        "chain": "eth",
        "order": "DESC",
        "address": wallet
    }
    result = evm_api.wallets.get_wallet_history(
        api_key=api_key,
        params=params,
    )
    
    rslt = str(result)
    with open(f'files/history{uid}.txt', 'w') as f:
        f.write(rslt)
        f.close()


def get_token_balances(wallet: str):
    params = {
        "chain": "eth",
        "exclude_spam": True,
        "address": wallet
        
    }
    result = evm_api.token.get_wallet_token_balances(
        api_key=api_key,
        params=params,
    )
    
    return result[:10] if len(result) > 10 else result


def get_wallet_worth(wallet: str):
    params = {
        "exclude_spam": True,
        "exclude_unverified_contracts": True,
        "address": wallet
    }
    
    result = evm_api.wallets.get_wallet_net_worth(
        api_key=api_key,
        params=params,
    )
    return result 

def wallet_pnl_breakdown(walllet: str, uid):
    params = {
    "chain": "eth",
    "address": walllet
    }

    result = evm_api.wallets.get_wallet_profitability(
    api_key=api_key,
    params=params,
    )
    rslt = str(result)
    with open(f'files/profits{uid}.txt', 'w') as f:
        f.write(rslt)
        f.close()
        
def token_bal(wallet, token_address = '0x27c78A7C10a0673C3509CCF63044AAb92E09edac'):
    params = {
        "chain": "eth",
        "token_addresses": [
            token_address
        ],
        "address": wallet
    }
    
    result = evm_api.token.get_wallet_token_balances(
        api_key=api_key,
        params=params,
    )
    r = result[0]['balance']
    return int(r)/10e18


def parse_tx(hash):
    
    params = {
        "chain": "eth",
        "transaction_hash": hash
    }
    result = evm_api.transaction.get_transaction(
        api_key=api_key,
        params=params,
    )
    value = float(result['value']) / 10**18
    return result['from_address'], result['to_address'], value


if __name__ == '__main__':
    w = '0x740e1B899F17b4619b0451Db5E3Ba3DC73131Fc3'
    tx = '0x62e2700b7b9d76f9cb0de904b3851293df09eaafa657f1b889f5e97db8a79930'
    p,y,u = parse_tx(tx)
    print(u)