#!/usr/bin/env python3

# needed python libs
import os
import math
import time
import ecdsa
import sys
import smtplib
import binascii
import multiprocessing
import ssl
from email.message import EmailMessage
from bitcoinlib.keys import HDKey
from bitcoinlib.services.services import Service

# import our configs
import addresses
import env

# do your job !
def hunter(num_seconds, worker_idx, return_dict):

    # construct a set (inkl. hashtable) from the list of addresses for fast search
    addresses_set = set(addresses.addresses)

    i = 0
    start = time.time()
    while ((time.time() - start)) < num_seconds:
        
        # generate a random BTC private key
        private_key = binascii.hexlify(os.urandom(32)).decode('utf-8')
        key = HDKey(private_key)

        # get the BTC address
        address = key.address()

        # check if the address in the list
        balance = str((Service().getbalance(address))/1e8) + " BTC"

        if balance == "0.0 BTC":
          pass
        else:
          lucky_text  = "--------------------------------------\n"
          lucky_text += "FOUND A LUCKY PAIR:\n" 
          lucky_text += "PRIVATE KEY = " + private_key + "\n"
          lucky_text += "ADDRESS = " + address + "\n"
          lucky_text += "BALANCE = " + balance + "\n"
          lucky_text += "--------------------------------------\n"

          fl = open(env.OUT_FILE, "a")
          fl.write(lucky_text)
          fl.close()

          print(lucky_text)
          break

        # increment
        i = i + 1
    
    # record the number of generated private keys
    return_dict[worker_idx] = i

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []
    
    if env.NUM_INSTANCES == 0:
        inst_count = multiprocessing.cpu_count()
    else:
        inst_count = env.NUM_INSTANCES

    for i in range(inst_count):
        p= multiprocessing.Process(target=hunter, args=(env.MAX_SECONDS, i, return_dict))
        processes.append(p)
        p.start()

    total = 0
    for i in range(inst_count):
        processes[i].join()
        proc_ret = return_dict[i]
        total += proc_ret

    rate = total/env.MAX_SECONDS
    print("Tried " + str(total) + " keys in " + str(env.MAX_SECONDS) + " seconds (" + str(math.floor(rate)) + " key/s).")
