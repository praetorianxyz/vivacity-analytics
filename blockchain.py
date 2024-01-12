from web3 import Web3
import requests

url = 'https://rpc.ansybl.io/canto/mainnet/evm_rpc/?X-API-KEY=1e2da94585e79feeb984d656'
w3 = Web3(Web3.HTTPProvider(url))


BLOCKS_PER_YEAR = 365 * 24 * 60 * 60 / 5.7

### Load Canto price from Coingecko
response = requests.get('https://api.coingecko.com/api/v3/simple/price',
    params={'ids': 'canto', 'vs_currencies': 'usd'}
)
canto_price_usd = response.json()['canto']['usd']

### Load cNOTE data from blockchain
contract_address_cnote = '0xEe602429Ef7eCe0a13e4FfE8dBC16e101049504C'

with open('vivacity-analytics/abis/cnote-contract-abi.txt', 'r') as f:
    contract_abi_cnote = f.read()

contract_cnote = w3.eth.contract(address=contract_address_cnote, abi=contract_abi_cnote)

def get_data_from_contract_cnote():
    supply_rate_per_block = contract_cnote.functions.supplyRatePerBlock().call()
    borrow_rate_per_block = supply_rate_per_block

    exchange_rate_stored = contract_cnote.functions.exchangeRateStored().call()

    return {
        'supplyRatePerBlock': supply_rate_per_block,
        'borrowRatePerBlock': borrow_rate_per_block,
        'exchangeRateStored': exchange_rate_stored,
    }

contract_data_cnote = get_data_from_contract_cnote()


### Load vcNOTE data from blockchain
contract_address_vcnote = '0x74c6dBA944702007e3a18C2caad9F6F274cF38dD'

with open('vivacity-analytics/abis/vcnote-contract-abi.txt', 'r') as f:
    contract_abi_vcnote = f.read()

contract_vcnote = w3.eth.contract(address=contract_address_vcnote, abi=contract_abi_vcnote)

def get_data_from_contract_vcnote():
    total_supply = contract_vcnote.functions.totalSupply().call()
    total_borrows = contract_vcnote.functions.totalBorrows().call()
    total_reserves = contract_vcnote.functions.totalReserves().call()

    supply_rate_per_block = contract_vcnote.functions.supplyRatePerBlock().call()
    borrow_rate_per_block = contract_vcnote.functions.borrowRatePerBlock().call()

    exchange_rate_stored = contract_vcnote.functions.exchangeRateStored().call()

    return {
        'totalSupply': total_supply,
        'totalBorrows': total_borrows,
        'totalReserves': total_reserves,
        'supplyRatePerBlock': supply_rate_per_block,
        'borrowRatePerBlock': borrow_rate_per_block,
        'exchangeRateStored': exchange_rate_stored,
    }

contract_data_vcnote = get_data_from_contract_vcnote()

interest_rate_model_vcnote = {
    'baseRatePerBlock': 0,
    'multiplierPerBlock': 1436903167,
    'kink': 800000000000000000,
    'jumpMultiplierPerBlock': 225306416726,
}


### Load chyVWEAX data from blockchain
contract_address_chyvweax = '0x6812636BF088798cB568D04F2dB4D2f34B039E11'

with open('vivacity-analytics/abis/chyvweax-contract-abi.txt', 'r') as f:
    contract_abi_chyvweax = f.read()

contract_chyvweax = w3.eth.contract(address=contract_address_chyvweax, abi=contract_abi_chyvweax)

def get_data_from_contract_chyvweax():
    total_supply = contract_chyvweax.functions.totalSupply().call()

    return {
        'totalSupply': total_supply,
        'totalBorrows': 0,
        'totalReserves': 0,
        'supplyRatePerBlock': 0,
        'borrowRatePerBlock': 0,
        'exchangeRateStored': 10**18,
    }

contract_data_chyvweax = get_data_from_contract_chyvweax()


### Load data from Price Oracle Router
contract_address_oracle = '0xFFFa8184EE41D7Ecf830b6e7A046C838747709C3'

with open('vivacity-analytics/abis/oracle-contract-abi.txt', 'r') as f:
    contract_abi_oracle = f.read()

contract_oracle = w3.eth.contract(address=contract_address_oracle, abi=contract_abi_oracle)

def get_data_from_contract_oracle(address_cToken):
    price = contract_oracle.functions.getUnderlyingPrice(address_cToken).call()

    return {
        'getUnderlyingPrice': price,
    }

contract_data_oracle_vcnote = get_data_from_contract_oracle(contract_address_vcnote)
contract_data_oracle_chyvweax = get_data_from_contract_oracle(contract_address_chyvweax)


### Load reward information from blockchain
contract_address_rewards = '0x85156B45B3C0F40f724637ebfEB035aFB29BD083'

with open('vivacity-analytics/abis/rewards-contract-abi.txt', 'r') as f:
    contract_abi_rewards = f.read()

contract_rewards = w3.eth.contract(address=contract_address_rewards, abi=contract_abi_rewards)

def get_data_from_contract_rewards(address_cToken):
    epoch_last_update = contract_rewards.functions.lendingMarketTotalBalanceEpoch(address_cToken).call()
    #lending_market_balance = contract_rewards.functions.lendingMarketTotalBalance(address_cToken, epoch_last_update).call()
    reward_information = contract_rewards.functions.rewardInformation(epoch_last_update).call()

    return {
        'rewardInformation': reward_information,
    }

contract_data_rewards = get_data_from_contract_rewards(contract_address_vcnote)


### Helper functions
def utilization(total_supply, total_borrows, total_reserves):
    return total_borrows / (total_supply - total_reserves)

def borrow_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier):
    return multiplier * min(utilization, kink) + jump_multiplier * max(0, utilization - kink) + base_rate

def supply_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier, reserve_factor):
    return borrow_interest_rate(utilization, base_rate, multiplier, kink, jump_multiplier) * utilization * (1 - reserve_factor)


### Prepare data
blockchain_data = {
    'CANTO': {
        'price': canto_price_usd,
    },
    'cNOTE': {
        'borrow_rate': contract_data_cnote['borrowRatePerBlock'] * BLOCKS_PER_YEAR / 10**18,
        'supply_rate': contract_data_cnote['supplyRatePerBlock'] * BLOCKS_PER_YEAR / 10**18,
    },
    'vcNOTE': {
        'base_rate': interest_rate_model_vcnote['baseRatePerBlock'] * BLOCKS_PER_YEAR / 10**18,
        'multiplier': interest_rate_model_vcnote['multiplierPerBlock'] * BLOCKS_PER_YEAR / 10**18,
        'kink': interest_rate_model_vcnote['kink'] / 10**18,
        'jump_multiplier': interest_rate_model_vcnote['jumpMultiplierPerBlock'] * BLOCKS_PER_YEAR / 10**18,

        'total_supply': contract_data_vcnote['totalSupply'], # unit: vcNOTE
        'total_borrows': contract_data_vcnote['totalBorrows'], # unit: cNOTE
        'total_reserves': contract_data_vcnote['totalReserves'], # unit: cNOTE
        'exchange_rate_stored': contract_data_vcnote['exchangeRateStored'], # unit: cNOTE per vcNOTE

        'underlying_price': contract_data_oracle_vcnote['getUnderlyingPrice'],
    },
    'chyVWEAX': {
        'total_supply': contract_data_chyvweax['totalSupply'], # unit chyVWEAX

        'underlying_price': contract_data_oracle_chyvweax['getUnderlyingPrice'],
    },
    'rewards': {
        'rewards_per_week': contract_data_rewards['rewardInformation'][1], # unit: CANTO
    }
}

blockchain_data['vcNOTE']['utilization'] = utilization(
    blockchain_data['vcNOTE']['total_supply'] * blockchain_data['vcNOTE']['exchange_rate_stored'],
    blockchain_data['vcNOTE']['total_borrows'],
    blockchain_data['vcNOTE']['total_reserves']
) * 10**18

blockchain_data['vcNOTE']['borrow_rate'] = borrow_interest_rate(
    blockchain_data['vcNOTE']['utilization'],
    blockchain_data['vcNOTE']['base_rate'],
    blockchain_data['vcNOTE']['multiplier'],
    blockchain_data['vcNOTE']['kink'],
    blockchain_data['vcNOTE']['jump_multiplier']
)

blockchain_data['vcNOTE']['supply_rate'] = supply_interest_rate(
    blockchain_data['vcNOTE']['utilization'],
    blockchain_data['vcNOTE']['base_rate'],
    blockchain_data['vcNOTE']['multiplier'],
    blockchain_data['vcNOTE']['kink'],
    blockchain_data['vcNOTE']['jump_multiplier'],
    0.1
)


def get_data_from_blockchain():
    return blockchain_data
