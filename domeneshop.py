#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import argparse
import os
import dns.resolver


from domeneshop.domeneshop import Domeneshop

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Path to config file')
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')

    args = parser.parse_args()
    config = args.config

    if config == None:
        config = os.path.dirname(os.path.realpath(__file__)) + "/config/domains.yml"

    if os.environ.get('CERTBOT_DOMAIN'):
        domain = str(os.environ.get('CERTBOT_DOMAIN'))
    else:   
        print ('No domain specified')
        return False

    if os.environ.get('CERTBOT_VALIDATION'):
        txt_record = str(os.environ.get('CERTBOT_VALIDATION'))
    else:
        print ('No validation string')
        return False

    object = Domeneshop(verbose=args.verbose, config=config)

    for record in object.config['record']:
        if domain == record['domain']:
          object.update_record(record['id'], domain, txt_record)

    print("Waiting for DNS-modification to propagate")
    time.sleep(30)   # delays for 30 seconds to wait for DNS-modification to propagate

if __name__ == "__main__":
    main()
