from flask import Blueprint, request, current_app
from backend.models import User, Transaction, Merchant
from backend import db, mail
import json
import requests
from datetime import datetime, timedelta
from flask_mail import Message
import random
import string
import bcrypt

transactions = Blueprint('transactions', __name__)


@transactions.route('/transactions/view', methods=['POST'])
def add_new_kid():
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
                          'merchant': Merchant.query.filter_by(id=x.merchant_id).first().name} for x in
                         Transaction.query.filter_by(user_id=user.id)]

    return json.dumps({'status': 1, 'transactions': all_transactions})
