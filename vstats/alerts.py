import sys
import json
import requests
import socket
from config import VSTATS_TOKEN,VALIDATOR_ADDR,TARGET_SLOT,TARGET_SLOT_FINAL,TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT,NUM_SLOTS,VSTATS_ALERT_REMOVE_KEY,VSTATS_ALERT_OUT_OF_ELECTION

VSTATS_API = "https://vstats.one/api/autobidder"

class Alerts:
    def __init__(self, VSTATS_API: str, connect_to_api: object) -> None:
        self.VSTATS_API = VSTATS_API
        self.connect_to_api = connect_to_api

    def send_to_vstats_start(self) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "type": "start",
            "hostname":socket.gethostname(),
            "address": VALIDATOR_ADDR,
            "target_slot": TARGET_SLOT,
            "target_slot_final": TARGET_SLOT_FINAL,
            "target_slot_final_enabled_blocks_left": TARGET_SLOT_FINAL_ENABLED_BLOCKS_LEFT
        }
        self.connect_to_api("", self.VSTATS_API, "", j=j)
    
    def send_to_vstats_generic(self,message:str) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "type": "generic",
            "address": VALIDATOR_ADDR,
            "hostname":socket.gethostname(),
            "message": message,        
        }
        self.connect_to_api("", self.VSTATS_API, "", j=j)
    
    def send_to_vstats_key_add(self,message:str) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "type": "key_add",
            "address": VALIDATOR_ADDR,
            "hostname":socket.gethostname(),
            "message": message,        
        }
        self.connect_to_api("", self.VSTATS_API, "", j=j)
        
    def send_to_vstats_key_remove(self,message:str) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "type": "key_remove",
            "address": VALIDATOR_ADDR,
            "hostname":socket.gethostname(),
            "message": message,        
        }
        full, _, _ = self.connect_to_api("", self.VSTATS_API, "", j=j)

    def send_to_vstats_out_of_election(self,target_slot:int,my_slot_range_end:int,key_to_remove:str,num_blocks_left:int) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "type": "out_of_election",
            "address": VALIDATOR_ADDR,
            "hostname":socket.gethostname(),
            "target_slot": target_slot, 
            "current_slot": my_slot_range_end,
            "key_to_remove":key_to_remove,
            "num_blocks_left":num_blocks_left 
        }
        self.connect_to_api("", self.VSTATS_API, "", j=j)
    
    def send_to_vstats_over_target(self,target_slot:int,my_slot_range_end:int,key_to_remove:str,num_blocks_left:int) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "type": "over_target",
            "address": VALIDATOR_ADDR,
            "hostname":socket.gethostname(),
            "target_slot": target_slot,  
            "current_slot": my_slot_range_end,
            "key_to_remove":key_to_remove,
            "num_blocks_left":num_blocks_left
        }
        self.connect_to_api("", self.VSTATS_API, "", j=j)
    
    def generic_error(self,e) -> None:
        j = {
            "api_token": VSTATS_TOKEN,
            "error": 'true',
            "hostname":socket.gethostname(),
        }
        self.connect_to_api("", self.VSTATS_API, "", j=j)


def connect_to_api(
    token: str,
    api: str,
    endpoint: str,
    call: requests = requests.get,
    j: dict = {},
) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(api + endpoint, headers=headers, json=j, verify=True)
    except json.decoder.JSONDecodeError as e:
        data = r.text
        
def vstats_slot_alerts(target_slot:int,my_slot_range:dict,key_to_remove:str,num_blocks_left:int) -> None:
    try:
        if(VSTATS_TOKEN):
            if(my_slot_range.end > NUM_SLOTS and VSTATS_ALERT_OUT_OF_ELECTION == True):
                try:
                    alerts.send_to_vstats_out_of_election(target_slot,my_slot_range.end,key_to_remove,num_blocks_left)
                except: 
                    pass
            elif(my_slot_range.end > target_slot and VSTATS_ALERT_REMOVE_KEY == True):   
                try:
                    alerts.send_to_vstats_over_target(target_slot,my_slot_range.end,key_to_remove,num_blocks_left)
                except: 
                    pass
            else:
                pass
    except:
        pass
        
def vstats_autobidder_start() -> None:
    if(VSTATS_TOKEN):
        try:
            alerts.send_to_vstats_start()
        except: 
            pass
               
alerts = Alerts(VSTATS_API, connect_to_api)
