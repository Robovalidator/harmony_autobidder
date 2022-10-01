import os
from bls_keys import BLS_KEYS

HOME = os.environ.get('HOME') or "."
NODE_API_URL = "https://api.s0.t.hmny.io"
# Set to False to query your own Node (Shard 0 is required)
USE_REMOTE_NODE = True

# Put your own validator address below
VALIDATOR_ADDR = ""

# vStatsToken: run /token on vstatsbot to generate
VSTATS_TOKEN=""
VSTATS_ALERT_REMOVE_KEY = False # Set to false if you do not want remove key alerts
VSTATS_ALERT_OUT_OF_ELECTION = True # Set to false if you do not want out of election alerts

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

BID_GAS_PRICE = 105

CHANGE_KEY_TIMEOUT_SECONDS = 10

REMAINING_BLOCKS_FOR_AUTO_DELEGATE = 200

# Set this to greater than 0 if you want the bot to change the bid
# at the last minute before epoch end
# 30 blocks per minute e.g 30 mins = 900
TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT = -900 
TARGET_SLOT_FINAL = 888

NUM_SLOTS = 900
NUM_SLOTS_TO_SHOW = 910

EPOS_UPPER_BOUND = 1.35
EPOS_LOWER_BOUND = 0.65
PREVENT_INEFFICIENT_BID = True
DEFAULT_INTERVAL_SECONDS = 5

# Map of validator address to validator details
VALIDATOR_DETAILS = {}
