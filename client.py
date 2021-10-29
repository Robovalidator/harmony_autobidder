from subprocess import PIPE, Popen
from time import sleep

import simplejson

import config
from config import HMY_PATH


class HarmonyClientError(Exception):
    pass


def get_json_for_command(process_args, retries=3, retry_wait=0.1):
    original_process_args = process_args[:]
    if config.USE_REMOTE_NODE:
        process_args.extend(["--node", config.NODE_API_URL])
    process = Popen(process_args, stdout=PIPE)
    (output, err) = process.communicate()
    try:
        return simplejson.loads(output)
    except simplejson.JSONDecodeError:
        sleep(retry_wait)
        print(f"Got an error in get_json_for_command({' '.join(process_args)}), output={output}, err={err}, "
              f"retrying after {retry_wait}s")
        if retries > 0:
            return get_json_for_command(original_process_args, retries=retries - 1, retry_wait=retry_wait * 1.25)
    return None


def get_validator_info(address):
    return get_json_for_command([HMY_PATH, "blockchain", "validator", "information", address], retries=25)


def get_all_validators_info_page(page):
    return get_json_for_command([HMY_PATH, "blockchain", "validator", "all-information", str(page)], retries=25)


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
    return get_json_for_command(
        base_process_args + ["--remove-bls-key", bls_key, "--timeout", str(config.CHANGE_KEY_TIMEOUT_SECONDS),
                             "--true-nonce"],
        retries=0
    )


def add_bls_key(bls_key, gas_price=config.BID_GAS_PRICE):
    base_process_args = _get_base_edit_validator_process_args(gas_price=gas_price)
    return get_json_for_command(
        base_process_args + ["--add-bls-key", bls_key, "--timeout", str(config.CHANGE_KEY_TIMEOUT_SECONDS),
                             "--true-nonce"],
        retries=0
    )
