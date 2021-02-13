import argparse
import csv
import json
from datetime import datetime, timedelta, timezone

import requests
from enums import OneUnit

import config

JSONRPC_ENDPOINT = "https://rpc.s0.t.hmny.io"


def main(main_args):
    write_csv(main_args.address, main_args.file)


def write_csv(address, csv_file):
    fieldnames = ("Date", "Action", "Account", "Symbol", "Volume", "Total", "Currency", "Memo")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    page_index = 0
    while 1:
        rows = get_transaction_history(address, page_index=page_index)
        print(rows)
        writer.writerows(rows)
        if not rows:
            break
        page_index += 1
    csv_file.close()

def get_transaction_history(address, page_index=0):
    params = [
        {
            "address": address,
            "pageIndex": page_index,
            "fullTx": True,
            "txType": "ALL",
            "order": "ASC"
        }
    ]

    payload = {
        "method": "hmyv2_getStakingTransactionsHistory",
        "params": params,
        "jsonrpc": "2.0",
        "id": 1,
    }
    response = requests.post(JSONRPC_ENDPOINT, json=payload).json()
    transactions = response['result']['staking_transactions']
    reward_transactions = [transaction for transaction in transactions if transaction['type'] == 'CollectRewards']
    action = "MINING"
    account = address
    symbol = "ONE"
    currency = "USD"
    rows = []
    for transaction in reward_transactions:
        dt_object = datetime.fromtimestamp(transaction['timestamp'], tz=timezone.utc)
        date = dt_object.strftime('%Y-%m-%d %H:%M:%S %z')
        hash = transaction['hash']
        memo = hash
        receipt_response = get_transaction_receipt(hash)
        volume = int(receipt_response['result']['logs'][0]['data'], 16) * OneUnit.Wei
        total = ''
        row = dict(Date=date, Action=action, Account=account, Symbol=symbol, Volume=volume, Total=total,
                   Currency=currency, Memo=memo)
        rows.append(row)
    return rows


def get_transaction_receipt(hash):
    params = [hash]

    # Example echo method
    payload = {
        "method": "hmyv2_getTransactionReceipt",
        "params": params,
        "jsonrpc": "2.0",
        "id": 1,
    }
    response = requests.post(JSONRPC_ENDPOINT, json=payload).json()
    return response


def usage():
    return """python taxes.py"""


def get_command_line_options():
    parser = argparse.ArgumentParser(description="Query staking taxes and output them to a Bitcoin.tax "
                                                 "CSV file.\n\n" + usage())
    parser.add_argument(
        '-a', '--address', help='address', type=str
    )
    parser.add_argument('-f', '--file', help='csv outputfile', type=argparse.FileType(mode='w'))
    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
