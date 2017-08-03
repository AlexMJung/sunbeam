#!/usr/bin/env python

import json
import sys
import csv

# throw away script to create a CSV of accounts from the json of a query of accounts

input = sys.stdin.read()

writer = csv.writer(sys.stdout)

skip_list = [u'Retained Earnings', u'Sales of Product Income', u'Services', u'Uncategorized Asset', u'Uncategorized Expense', u'Uncategorized Income', u'Undeposited Funds', u'Opening Balance Equity']

for account in json.loads(input)["QueryResponse"]["Account"]:
    if account['FullyQualifiedName'] not in skip_list:
        writer.writerow([
            account.get("FullyQualifiedName", ""),
            account.get("Classification", ""),
            account.get("AccountType", ""),
            account.get("AccountSubType", ""),
            account.get("Description", "")
        ])
