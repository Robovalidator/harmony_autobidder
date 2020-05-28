# harmony_autobidder

## About

Harmony AutoBidder automatically manages BLS keys for your validator
to ensure you stay within a slot range while you sleep. If you've benefited from using 
this program please consider donating or delegating ONEs to RoboValidator at 
https://staking.harmony.one/validators/one1x8fhymx4xsygy4dju9ea9vhs3vqg0u3ht0nz74. Also
checkout our website at https://robovalidator.com

## Setup
### Download the hmy client if you haven't already
```
$ cd ~/
$ mkdir ~/harmony
$ cd ~/harmony
$ curl -LO https://harmony.one/hmycli && mv hmycli hmy && chmod +x hmy
```
You don't have to use `~/harmony` but that's how the service is currently configured.
See `config.py` if you'd like to modify the path setttings.

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
`USE_REMOTE_NODE = False`
2. Set `VALIDATOR_ADDR` to your validator's address
3. Set `BLS_KEYS` to contain all your bls key string in order of highest priority. The keys will be added and removed as if this list was a stack.
4. Configure `MAX_SLOT` and `MIN_SLOT` to your liking. Note that the `MIN_SLOT` config works as a guideline and the bot will never adjust the keys in a way that puts you below `MAX_SLOT`.
5. `MAX_VALIDATORS_PAGES` is the maximum number of validator pages the client can scan for downloading validator info
6. You still need to make sure your nodes are setup to run with all the BLS keys assigned to the validator between epoch changes

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
BLS keys: f82d30adadabaaaeba00406a5d607134343888dccf4fc45bdc22f02ad10df3ddeed1656a2a253262dae92095297e3f84, 710366b83f9d120a763f2e68c994e10033940ddf7ec0eeefef3d4c990dd5d45f4c7d7ccc7ca67d99f0e40c354e539e00
If we lower the bid by adding key the slots will be: 366-368
If we increase the bid by removing a key the slots will be: 28
....
```
The bot will poll for validator information every five seconds and output the state again if anything changes.

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
