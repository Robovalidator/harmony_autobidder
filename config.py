import os

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

# Add your BLS keys here in order of priority across ALL nodes
BLS_KEYS = (
    # Shard 0
    "710366b83f9d120a763f2e68c994e10033940ddf7ec0eeefef3d4c990dd5d45f4c7d7ccc7ca67d99f0e40c354e539e00",
    "f82d30adadabaaaeba00406a5d607134343888dccf4fc45bdc22f02ad10df3ddeed1656a2a253262dae92095297e3f84",
    "8be0121e5282071287886b07af678eefb67737f12d306c370f588d2612bf3020f9dc97fce63ee86c0ee3cd2153e43f90",
    "2bcee590cb191a7bff14641fb0afdd6e07ee83b45e7247fce9dcf0fc10d8c7c3560dad54891cdf8bffff36e4a2c24f04",

    # Shard 1
    "1fd87fa97fb1f0558fc59bd58b3400cac7b8297f7357a8ac633a035fe54b743de0a88122c837bc3cd81351772a3f9419",
    "84410bce01d1cc0a79832f8bef3196d9aa948dcb32df76c7111f2399a8592713dfffffd582f6452136a4fc4de0bede11",
    "4191653833ccc87bdc4f30a83709b4ee3a54f2cee422485e1f7688fbee5d5b22ab1c447ffaab1c160f29290de697a719",
    "b39a795169c5a144779e7acd614f039b6c0e4c9ed918e9b91bd4ef9b611f7421bba2472fd41e10acd0541d1d2ad0b981",

    # Shard 2
    "1efe44ddb21ca28cf2d15e357a0ea292e57bea000981f2f467163030cf70549412c0529a3cf774d9eced7e61526ff402",
    "202770994a16d8bf6ed5d8c11985302352e5a9739588236c0d4d1a2a99c2dc97a74542b7cd30a7f6515b6e36a44f8c86",
    "6acba8d25c242f6f951b532846540c0fbca3d1de18c5adc86ff69e5e90fe099ff6f3a2bfa2ab69d450323a5ebcc5c916",
    "dbeadb874e853645f7010be775bff281edca340c6067c390fbdaab6aa3b97ce86c874ad778c6520935354f770a40ce0e"
)

# Maximum allowable slot
MAX_SLOT = 318

# Minimum slot to shoot for as long as removing a key doesn't move us past the MAX_SLOT
MIN_SLOT = 100

# Maximum validator pages to parse
MAX_VALIDATORS_PAGES = 50

# Ignore validators below the given bid
VALIDATOR_MIN_BID = 200000

# Path to base web page html contents
BASE_HTML_PATH = "{}/harmony/robovalidator.html".format(HOME)

BID_GAS_PRICE = 2

