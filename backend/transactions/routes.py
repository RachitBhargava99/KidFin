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
from backend.transactions.utils import satisfy_amount_condition, satisfy_gps_condition, get_merchant_information,\
    process_purchase, get_purchase_data, has_balance, get_curr_balance

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
            nessie_transactions = get_purchase_data(kid_user.accountId)
            all_transactions += [{'name': kid_user.name,
                                  'amount': x[1],
                                  'merchant': x[0],
                                  'date': x[2]} for x in nessie_transactions]

#            all_transactions += [{'name': kid_user.name,
#                                  'amount': x.amount,
#                                  'merchant': Merchant.query.filter_by(merchant_id=x.merchant_id).first().name,
#                                  'date': x.timestamp.strftime('%Y-%m-%d')} for x in
#                                 Transaction.query.filter_by(user_id=kid_user.id)]
#    all_transactions += [{'name': user.name,
#                          'amount': x.amount,
#                          'merchant': Merchant.query.filter_by(merchant_id=x.merchant_id).first().name,
#                          'date': x.timestamp.strftime('%Y-%m-%d')} for x in
#                         Transaction.query.filter_by(user_id=user.id)]

    nessie_transactions = get_purchase_data(user.accountId)

    all_transactions += [{'name': user.name,
                          'amount': x[1],
                          'merchant': x[0],
                          'date': x[2]} for x in nessie_transactions]

    return json.dumps({'status': 1, 'transactions': all_transactions})


@transactions.route('/transactions/process', methods=['POST'])
def process_transaction():
    """Processes a new transaction

    Method Type: POST

    Special Restrictions
    --------------------
    Account restrictions must not prevent the transaction
    Account must have enough funds for the transaction

    JSON Parameters
    ---------------
    account_id : str
        Account ID to debit
    amount : int
        Amount to debit
    merchant_id : str
        ID of merchant initiating the transaction

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure

    """
    request_json = request.get_json()

    account_id = request_json['account_id']
    amount = request_json['amount']
    merchant_id = request_json['merchant_id']

    user = User.query.filter_by(accountId=account_id).first()

    if user is None:
        return json.dumps({'status': 0, 'error': "The provided account does not exist."})

    # Get Merchant Details using Nessie
    merchant_cats, curr_coordinates = get_merchant_information(merchant_id)

    if not has_balance(account_id, amount):
        return json.dumps({'status': 0, 'error': "Insufficient Balance"})

    if user.isParent:
        # Process transaction using Nessie
        transaction_status = process_purchase(user.accountId, merchant_id, amount)
    else:
        all_restrictions = Restriction.query.filter_by(user_id=user.id, isActive=True)

        cat_check = False
        gps_check = False

        for restriction in all_restrictions:
            if not satisfy_amount_condition(restriction, amount):
                return json.dumps({'status': 0, 'error': "Card Restricted"})
            if restriction.cat_id in merchant_cats and not cat_check:
                cat_check = True
            if restriction.primary_location is None or (satisfy_gps_condition(restriction, curr_coordinates) and not gps_check):
                gps_check = True

        if cat_check and gps_check:
            transaction_status = process_purchase(user.accountId, merchant_id, amount)
        else:
            print("Card Restricted")
            return json.dumps({'status': 0, 'error': "Card Restricted"})

    if not transaction_status:
        return json.dumps({'status': 0, 'error': "Transaction Failure"})

    new_transaction = Transaction(user_id=user.id, amount=amount, merchant_id=merchant_id)
    db.session.add(new_transaction)
    db.session.commit()

    return json.dumps({'status': 1})


@transactions.route('/transactions/curr_balance', methods=['POST'])
def get_current_balance():
    """Gets current account balance

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
        balance : int
            Current account balance

    """
    request_json = request.get_json()

    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)

    if user is None:
        return json.dumps({'status': 0, 'error': "User Not Authenticated"})

    curr_balance = get_curr_balance(user.accountId)

    return json.dumps({'status': 1, 'balance': curr_balance})
