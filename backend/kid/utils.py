from datetime import timedelta
from sqlalchemy import and_
import random
import math
from backend import db
from datetime import datetime


def transfer_money(payer_accountID, payee_accountID, amount, date=datetime.now().strftime('%Y-%d-%m')):
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

    return response.json()['code'] == 201
