from datetime import timedelta
from sqlalchemy import and_
import random
import math
from backend import db
from datetime import datetime
import requests


def transfer_money(payer_accountID, payee_accountID, amount, date=datetime.now().strftime('%Y-%m-%d')):
    #   Purpose: Transfers money from payer to payee
    #
    #   Inputs:
    #   payer_accountID (string)
    #   payee_accountID (string)
    #   amount (string)
    #   date (optional string: YYYY-DD-MM)
    #   assumptions- medium: balance, status: pending, description: ""

    url = "http://api.reimaginebanking.com/accounts/" + payer_accountID +\
          "/transfers?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    payload = {
        "medium": "balance",
        "payee_id": payee_accountID,
        "amount": amount,
        "transaction_date": date,
        "status": "pending",
        "description": " "
    }

    response = requests.post(url, json=payload)
    print(response.json())

    return response.json()['code'] == 201


def add_account(customerID, accountName, balance, accountNumber):
    #   Purpose: Creates an account with a given customerID
    #
    #   Inputs:
    #   customerID (string)
    #   account_name (string)
    #   balance (integer)
    #   account_number (string) - a 16 digit string that is essentially the 'credit card number'; make it anything
    #   assumptions- type: checking, rewards: 0

    url = "http://api.reimaginebanking.com/customers/" + customerID + "/accounts?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    payload = {
        "type": "Checking",
        "nickname": accountName,
        "rewards": 0,
        "balance": balance,
        "account_number": accountNumber
    }

    response = requests.post(url, json=payload)

    return response.json()['objectCreated']['_id']
