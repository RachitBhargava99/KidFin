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


def getMerchantCategory(merchantID):
    #   Purpose: Returns categories merchant belongs to in a list
    #
    #   Inputs:
    #   merchantID (string)

    url = "http://api.reimaginebanking.com/merchants/59394f0aceb8abe242517929?key=bb72fd1c5dee869a93bd5c6ba281cadb"

    response = requests.get(url)

    return (response.json())["category"]


def processPurchase(accountID, merchantID, amount, date = "2019-05-24"):
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

    response = requests.get(url)

    return response.text
