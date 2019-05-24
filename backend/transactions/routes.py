from flask import Blueprint, request, current_app
from backend.models import User, Transaction, Merchant, Restriction
from backend import db, mail
import json
import requests
from datetime import datetime, timedelta
from flask_mail import Message
import random
import string
import bcrypt
from backend.transactions.utils import satisfy_amount_condition, satisfy_gps_condition

transactions = Blueprint('transactions', __name__)


@transactions.route('/transactions/view', methods=['POST'])
def view_transactions():
    """Shows all transactions linked to an account

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure
        transactions: list of dicts of transactions
            name: str
                Name of the user who made the transaction
            amount: int
                Amount of transaction
            merchant: str
                Name of the merchant who initiated the transaction
            date: str
                Date of transaction

    """
    request_json = request.get_json()

    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)

    if user is None:
        return json.dumps({'status': 0, 'error': "User Not Authenticated"})

    all_transactions = []

    if user.isParent:
        all_users = User.query.filter_by(parent_id=user.id)
        for kid_user in all_users:
            all_transactions += [{'name': kid_user.name,
                                  'amount': x.amount,
                                  'merchant': Merchant.query.filter_by(id=x.merchant_id).first().name} for x in
                                 Transaction.query.filter_by(user_id=kid_user.id)]
    else:
        all_transactions += [{'name': user.name,
                              'amount': x.amount,
                              'merchant': Merchant.query.filter_by(id=x.merchant_id).first().name,
                              'date': x.timestamp.strftime('%B %d, %Y')} for x in
                             Transaction.query.filter_by(user_id=user.id)]

    return json.dumps({'status': 1, 'transactions': all_transactions})


@transactions.route('/transactions/process', methods=['POST'])
def process_transaction():
    """Processes a new transaction

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in

    JSON Parameters
    ---------------
    accountId : str
        Account ID to debit
    amount : double
        Amount to debit

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure

    """
    request_json = request.get_json()

    accountId = request_json['accountId']
    amount = request_json['amount']
    curr_coordinates = request_json['curr_coordinates']
    merchant_id = request_json['merchant_id']

    user = User.query.filter_by(accountId=accountId).first()

    if user is None:
        return json.dumps({'status': 0, 'error': "The provided account does not exist."})

    # Get Merchant Details using Nessie

    if user.isParent:
        # Process transaction using Nessie
        pass
    else:
        all_restrictions = Restriction.query.filter_by(user_id=user.id)

        cat_check = False
        gps_check = False

        for restriction in all_restrictions:
            if not satisfy_amount_condition(restriction, amount, curr_coordinates):
                return json.dumps({'status': 0, 'error': "Card Restricted"})
            if restriction.cat_id in merchant_cats and not cat_check:
                cat_check = True
            if satisfy_gps_condition(restriction, curr_coordinates) and not gps_check:
                gps_check = True

        if check:
            # Process transaction using Nessie
        else:
            return json.dumps({'status': 0, 'error': "Card Restricted"})

    return json.dumps({'status': 1})
