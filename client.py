import config
from subprocess import PIPE, Popen
import simplejson


class HarmonyClientError(Exception):
    pass


def get_json_for_command(process_args):
    if config.USE_REMOTE_NODE:
        process_args.extend(["--node", config.NODE_API_URL])
    process = Popen(process_args, stdout=PIPE)
    (output, err) = process.communicate()
    try:
        return simplejson.loads(output)
    except simplejson.JSONDecodeError:
        raise HarmonyClientError(output)


def get_validator_info(address):
    return get_json_for_command(["hmy", "blockchain", "validator", "information", address])


def get_all_validators_info_page(page):
    return get_json_for_command(["hmy", "blockchain", "validator", "all-information", str(page)])


def get_latest_header():
    return get_json_for_command(["hmy", "blockchain", "latest-header"])


def _get_base_edit_validator_process_args():
    return ["hmy", "staking", "edit-validator",
            "--validator-addr", config.VALIDATOR_ADDR,
            "--passphrase-file", config.PASSPHRASE_PATH,
            "--bls-pubkeys-dir", config.BLS_ALL_KEYS_PATH]


def remove_bls_key(bls_key):
    base_process_args = _get_base_edit_validator_process_args()
    return get_json_for_command(base_process_args + ["--remove-bls-key", bls_key])


def add_bls_key(bls_key):
    base_process_args = _get_base_edit_validator_process_args()
    return get_json_for_command(base_process_args + ["--add-bls-key", bls_key])