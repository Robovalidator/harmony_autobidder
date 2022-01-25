import os
from bls_keys import BLS_KEYS

HOME = os.environ.get('HOME') or "."
NODE_API_URL = "https://api.s0.t.hmny.io"
# Set to False to query your own Node (Shard 0 is required)
USE_REMOTE_NODE = True

# Put your own validator address below
VALIDATOR_ADDR = "one1x8fhymx4xsygy4dju9ea9vhs3vqg0u3ht0nz74"

# Path to harmony CLI
HMY_PATH = "{}/harmony/hmy".format(HOME)

# Path to passphrase file
PASSPHRASE_PATH = "{}/harmony/passphrase.txt".format(HOME)

# Place all your bls .key and .pass files across ALL nodes in the directory below
# This is usually a superset of the keys in the .hmy/blskeys path which contains the keys
# for running a specific node
BLS_ALL_KEYS_PATH = "{}/harmony/.hmy/allkeys".format(HOME)

# The slot to target
TARGET_SLOT = 800

# Maximum validator pages to parse
MAX_VALIDATORS_PAGES = 10

# Path to base web page html contents
BASE_HTML_PATH = "{}/harmony/robovalidator.html".format(HOME)

BID_GAS_PRICE = 30

CHANGE_KEY_TIMEOUT_SECONDS = 10

REMAINING_BLOCKS_FOR_AUTO_DELEGATE = 1800

# Set this to greater than 0 if you want the bot to change the bid
# at the last minute before epoch end
BOTTOM_FEED_ENABLED_BLOCKS_LEFT = -100
BOTTOM_FEED_SLOT_DISTANCE = 25
NUM_SLOTS = 900
NUM_SLOTS_TO_SHOW = 910

EPOS_UPPER_BOUND = 1.35
EPOS_LOWER_BOUND = 0.65
PREVENT_INEFFICIENT_BID = True
DEFAULT_INTERVAL_SECONDS = 5
