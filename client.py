from subprocess import PIPE, Popen
from time import sleep

import simplejson

import config
from config import HMY_PATH


class HarmonyClientError(Exception):
    pass


def get_json_for_command(process_args, retries=3):
    if config.USE_REMOTE_NODE:
        process_args.extend(["--node", config.NODE_API_URL])
    process = Popen(process_args, stdout=PIPE)
    (output, err) = process.communicate()
    try:
        return simplejson.loads(output)
    except simplejson.JSONDecodeError:
        sleep(0.1)
        print("Got an error in get_json_for_command({}), output={} err={} retrying..".format(process_args, output, err))
        if retries > 0:
            get_json_for_command(process_args, retries=retries - 1)
        # raise HarmonyClientError(output)


def get_validator_info(address):
    return get_json_for_command([HMY_PATH, "blockchain", "validator", "information", address])


def get_all_validators_info_page(page):
    return get_json_for_command([HMY_PATH, "blockchain", "validator", "all-information", str(page)])


def get_latest_header():
    return get_json_for_command([HMY_PATH, "blockchain", "latest-header"])


def _get_base_edit_validator_process_args(gas_price=config.BID_GAS_PRICE):
    return [HMY_PATH, "staking", "edit-validator",
            "--validator-addr", config.VALIDATOR_ADDR,
            "--passphrase-file", config.PASSPHRASE_PATH,
            "--bls-pubkeys-dir", config.BLS_ALL_KEYS_PATH,
            "--gas-price", str(gas_price)]


def remove_bls_key(bls_key, gas_price=config.BID_GAS_PRICE):
    base_process_args = _get_base_edit_validator_process_args(gas_price=gas_price)
    return get_json_for_command(base_process_args + ["--remove-bls-key", bls_key])


def add_bls_key(bls_key, gas_price=config.BID_GAS_PRICE):
    base_process_args = _get_base_edit_validator_process_args(gas_price=gas_price)
    return get_json_for_command(base_process_args + ["--add-bls-key", bls_key])
