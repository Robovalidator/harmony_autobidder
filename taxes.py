import argparse
import csv
import json
from datetime import datetime, timedelta, timezone

import requests
from enums import OneUnit

import config

JSONRPC_ENDPOINT = "https://rpc.s0.t.hmny.io"


def main(main_args):
    write_csv(main_args.address, main_args.file, main_args.start_page, main_args.end_page)


def write_csv(address, csv_file, start_page, end_page):
    fieldnames = ("Date", "Action", "Account", "Symbol", "Volume", "Total", "Currency", "Memo")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for page_index in range(start_page, end_page + 1):
        rows = get_transaction_history(address, page_index=page_index)
        print(page_index)
        print(rows)
        writer.writerows(rows)
        page_index += 1
        if not rows:
            break
    csv_file.close()
    print("Generated bitcoin.tax file {}".format(csv_file.name))

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
    return """python taxes.py -a <validator_address> -f <output_filename>"""


def get_command_line_options():
    parser = argparse.ArgumentParser(description="Query staking taxes and output them to a Bitcoin.tax "
                                                 "CSV file.\n\n" + usage())
    parser.add_argument(
        '-a', '--address', help='address', type=str
    )
    parser.add_argument('-f', '--file', help='csv outputfile', type=argparse.FileType(mode='w'), default='staking_taxes.csv')
    parser.add_argument('-s', '--start_page', help='starting page index', type=int, default=0)
    parser.add_argument('-e', '--end_page', help='end page index', type=int, default=9999999)
    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
