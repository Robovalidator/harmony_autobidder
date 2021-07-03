# harmony_autobidder

## About

Harmony AutoBidder automatically manages BLS keys for your validator
to ensure you stay within a slot range while you sleep. It polls
for validator information regularly and decides to either remove or
add bls keys to stay within a slot range. The polling interval
starts slow and contracts as the end of the current epoch approaches.

If you've benefited from using this program please consider donating or delegating ONEs to RoboValidator at 
https://staking.harmony.one/validators/mainnet/one1x8fhymx4xsygy4dju9ea9vhs3vqg0u3ht0nz74 so we can continue
to improve this software.

## Setup
### Download the hmy client if you haven't already
```
$ cd ~/
$ mkdir ~/harmony
$ cd ~/harmony
$ curl -LO https://harmony.one/hmycli && mv hmycli hmy && chmod +x hmy
```
You don't have to use `~/harmony` but that's how the service is currently configured.
See `config.py` if you'd like to modify the path settings. Also make sure `$HOME/harmony` is 
in your system path.

### Create your passphrase.txt file
```
$ echo 'passphrase' > ~/harmony/passphrase.txt
$ chmod og-rw ~/harmony/passphrase.txt
```

### Copy BLS .key and .pass files into .hmy/allkeys
```
$ mkdir ~/harmony/.hmy/allkeys
$ cp ~/harmony/.hmy/blskeys/*.* ~/harmony/.hmy/allkeys
$ chmod og-rw ~/harmony/.hmy/allkeys/*.*
$ # Copy any other bls .key and .pass files from other nodes to ~/harmony/.hmy/allkeys as well
```

### Setup config.py 
1. If you are running a node on shard 0 on the same machine you can set
`USE_REMOTE_NODE = False` otherwise you need to set it to `True` since a lot of RPCs we use only work on shard 0.
2. Set `VALIDATOR_ADDR` to your validator's address
3. Set `BLS_KEYS` to contain all your bls key string in order of highest priority. The keys will be added and removed as if this list was a stack.
4. Configure `TARGET_SLOT` to your liking. The bot will try to adjust the keys in a way that puts you just at or above `TARGET_SLOT`.
5. If `PREVENT_INEFFICIENT_BID` is set to True the bot will try it's hardest to never overbid while keeping you elected.   
6. `MAX_VALIDATORS_PAGES` is the maximum number of validator pages the client can scan for downloading validator info
7. You still need to make sure your nodes are setup to run with all the BLS keys assigned to the validator between epoch changes

### Create a tmux session
```
$ tmux new-session -s autobidder
```

### Start the autobidding service
```
$ autobid.py
...
384: kaparnos (1019000)
385: FNHarmonyOS (1000000)
386: BBIT (545000)
387: FANIN5050-000001 (500452)
388: Total Harmony (488966)
389-404: InfStones (444438)
405: HarmonyFans - 1% FEE 🚀 (350337)
406: CONTABO-1#I´m sorry to all my Delegators,please undelegate ASAP.I´m closing this Validator#With 99.76% & fee 0.1%  :-((( # (281725)
407-410: Omen OS (DMun) (252500)
411: Coff33Blak (243647)
Name: RoboValidator.com
Current slots: 301-302
Current epoch uptime: 98.86814%
Current bid: 5506999
If we lower the bid by adding key the slots will be: 366-368
If we increase the bid by removing a key the slots will be: 28
....
```
The bot will poll for validator information every several seconds and output the state again if anything changes.

## Script options
```
$ autobid.py --help
usage: autobid.py [-h] [-o] [-l] [-j] [-e]

Autobidding service for harmony validators. python autobid.py

optional arguments:
  -h, --help          show this help message and exit
  -o, --once          Whether or not to run once
  -l, --html          Whether or not to print html
  -j, --json          Whether or not to output json
  -e, --raise_errors  Whether or not to let errors stop execution
  -d, --disable_bidding  If set then disable bidding and just output information
```
