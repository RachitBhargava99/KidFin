from datetime import timedelta
from sqlalchemy import and_
import random
import math
from backend import db
from backend.models import Restriction
from gencoder.polycoder import super_encoder
import requests


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
