from datetime import timedelta
from sqlalchemy import and_
import random
import math
from backend import db
from backend.models import Restriction
from gencoder.polycoder import super_encoder
import requests
from datetime import datetime


def satisfy_amount_condition(restriction, amount):
    if restriction.amount and restriction.amount < amount:
        return False
    return True


def satisfy_gps_condition(restriction, coordinates):
    curr_coordinates = super_encoder([f'{coordinates[0]}, {coordinates[1]}'])
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&' \
        f'origins={restriction.primary_location}&destinations=enc:{curr_coordinates}:&' \
        f'key=AIzaSyAhC98vcXbcu6cXoLWd4Dh0p1xNRtZ7xf0'
    maps_data = requests.get(url).json()
    distance = maps_data['rows'][0]['elements'][0]['distance']['value'] / 1000
    return restriction.distance >= distance


def get_merchant_category(merchantID):
    #   Purpose: Returns categories merchant belongs to in a list
    #
    #   Inputs:
    #   merchantID (string)

    url = "http://api.reimaginebanking.com/merchants/59394f0aceb8abe242517929?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    response = requests.get(url)

    return (response.json())["category"]


def process_purchase(accountID, merchantID, amount, date=datetime.now().strftime('%Y-%d-%m')):
    #   Purpose: Processes the purchase between the account and merchant
    #
    #   Inputs:
    #   accountID (string)
    #   merchantID (string)
    #   amount (string)
    #   date (optional string: YYYY-DD-MM)
    #   assumptions- medium: balance, status: pending, description: " "

    url = "http://api.reimaginebanking.com/accounts/" + accountID + "/purchases?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    payload = {
        "merchant_id": merchantID,
        "medium": "balance",
        "purchase_date": date,
        "amount": amount,
        "status": "pending",
        "description": " "
    }

    response = requests.post(url, json=payload)

    return response.json()['code'] == 201


def addAccount(customerID, accountName, balance, accountNumber):
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

    return response.text


def createCustomer(firstName, lastName, streetNum, streetName, city, state, zip):
    #   Purpose: Creates a customer with name and address information
    #
    #   Inputs:
    #   firstName (string)
    #   lastName (string)
    #   streetNum (string)
    #   streetName (string)
    #   city (string)
    #   state (string) - two letter abbreviated state code
    #   zip (string) - five digit zip code

    url = "http://api.reimaginebanking.com/customers?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    payload = {
        "first_name": firstName,
        "last_name": lastName,
        "address": {
            "street_number": streetNum,
            "street_name": streetName,
            "city": city,
            "state": state,
            "zip": zip
        }
    }

    response = requests.post(url, json=payload)

    return response.text


def getAccountData(customerID):
    #   Purpose: Returns information for all accounts associated with the given customerID
    #
    #   Inputs:
    #   customerID (string)

    url = "http://api.reimaginebanking.com/customers/" + customerID + "/accounts?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    response = requests.get(url)

    return response.text