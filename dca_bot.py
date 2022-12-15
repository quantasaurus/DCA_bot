from tinyman.v1.client import TinymanMainnetClient, TinymanClient
from algosdk.v2client.algod import AlgodClient
from time import sleep

# Add your address and private key here
# Do not share with anyone or upload to a repository!
account = {
    # TODO: add mnemonic support
    "address": "",
    "private_key": "",
}
algod = AlgodClient(
    algod_address="https://node.algoexplorerapi.io",
    algod_token="",
    headers={"User-Agent": "algosdk"},
)


client = TinymanClient(
    algod_client=algod, validator_app_id=552635992, user_address=account["address"]
)

# Assign both ASAs, get their tinyman pool
BULO, ALGO = client.fetch_asset(498684064), client.fetch_asset(0)
pool = client.fetch_pool(BULO, ALGO)
buys = 0
while True:
    try:
        # Get a quote for a swap of 10 ALGO to BULO with 1% slippage tolerance
        quote = pool.fetch_fixed_input_swap_quote(ALGO(10_000_000), slippage=0.01)
        print(quote)
        print(f"BULO per ALGO: {quote.price}")
        print(f"BULO per ALGO (worst case): {quote.price_with_slippage}")
        buys += 1
    except:
        pass

    try:
        print(f"Swapping {quote.amount_in} to {quote.amount_out_with_slippage}")
        # Prepare a transaction group
        transaction_group = pool.prepare_swap_transactions_from_quote(quote)
        # Sign the group with our key
        transaction_group.sign_with_private_key(
            account["address"], account["private_key"]
        )
        # Submit transactions to the network and wait for confirmation
        result = client.submit(transaction_group, wait=True)
    except:
        pass

    try:
        # Check if any excess remaining after the swap
        excess = pool.fetch_excess_amounts()
        if BULO in excess:
            amount = excess[BULO]
            print(f"Excess: {amount}")
            # This will redeem for any amount over 1000 BULO.  The idea being that you don't want to redeem after every single buy but
            # wait for some reasonable amount to build up.
            if amount > 1000:
                transaction_group = pool.prepare_redeem_transactions(amount)
                transaction_group.sign_with_private_key(
                    account["address"], account["private_key"]
                )
                result = client.submit(transaction_group, wait=True)
                print("transaction submitted")
    except:
        print("problem here or no excess, boss")
        pass
    print(f"buys: {buys}")
    print("sleeping")
    sleep(3600)
