import argparse
import csv
from datetime import datetime, timezone

import requests
from enums import OneUnit
from simplejson.errors import JSONDecodeError
from retry import retry

JSONRPC_ENDPOINT = "https://rpc.s0.t.hmny.io"


def main(main_args):
    write_csv(main_args.address, main_args.file, main_args.start_page, main_args.end_page, main_args.year)


def write_csv(address, csv_file, start_page, end_page, year_restrict):
    fieldnames = ("Date", "Action", "Account", "Symbol", "Volume", "Total", "Currency", "Memo")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    hashes = set()
    all_rows = []
    # The RPC is flaky and drops transactions so keep looping and
    # adding new rows until we cannot find any more rows
    while True:
        rows_added = 0
        for page_index in range(start_page, end_page + 1):
            rows, transactions = get_transaction_history(address, page_index=page_index, year_restrict=year_restrict)
            unique_rows = []
            for row in rows:
                hash = row['Memo']
                if hash in hashes:
                    continue
                hashes.add(hash)
                unique_rows.append(row)
                print(row['Date'])
            all_rows.extend(unique_rows)
            print(f"Page index: {page_index} rows: {len(unique_rows)}")
            rows_added += len(unique_rows)
            page_index += 1
            if not transactions:
                break
        print(f"Added {rows_added} this run.")
        if rows_added == 0:
            break
    all_rows.sort(key=lambda row: row['Date'])
    writer.writerows(all_rows)
    csv_file.close()
    print("Generated bitcoin.tax file {}".format(csv_file.name))


@retry((JSONDecodeError, requests.exceptions.SSLError), delay=1, tries=100)
def get_transaction_history(address, page_index=0, year_restrict=None):
    params = [
        {
            "address": address,
            "pageIndex": page_index,
            "pageSize": 1000,
            "fullTx": True,
            "txType": "SENT",
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
        if year_restrict and dt_object.year != year_restrict:
            continue
        date = dt_object.strftime('%Y-%m-%d %H:%M:%S %z')
        hash = transaction['hash']
        memo = hash
        receipt_response = get_transaction_receipt(hash)
        volume = int(receipt_response['result']['logs'][0]['data'], 16) * OneUnit.Wei
        total = ''
        row = dict(Date=date, Action=action, Account=account, Symbol=symbol, Volume=volume, Total=total,
                   Currency=currency, Memo=memo)
        rows.append(row)
    return rows, transactions


@retry((JSONDecodeError, requests.exceptions.SSLError), delay=1, tries=100)
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
        '-a', '--address', help='address', type=str, required=True
    )
    parser.add_argument('-f', '--file', help='csv outputfile', type=argparse.FileType(mode='w'), default='staking_taxes.csv')
    parser.add_argument('-s', '--start_page', help='starting page index', type=int, default=0)
    parser.add_argument('-e', '--end_page', help='end page index', type=int, default=9999999)
    parser.add_argument('-y', '--year', help='year to restrict to', type=int)
    return parser.parse_args()


if __name__ == '__main__':
    main_args = get_command_line_options()
    main(main_args)
