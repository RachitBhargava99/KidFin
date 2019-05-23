from flask import Blueprint, request, current_app
from backend.models import User, Restriction
from backend import db, mail
import json
import requests
from datetime import datetime, timedelta
from flask_mail import Message
import random
import string
import bcrypt

kid = Blueprint('kid', __name__)


# Checker to see whether or not is the server running
@kid.route('/event', methods=['GET'])
def checker():
    return "Hello"


@kid.route('/kid/add', methods=['POST'])
def add_new_kid():
    """Adds a new kid account, links it to the database, and sends them their login credentials

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in
    User must be parent

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    kid_name : str
        Name of the kid being added
    kid_email : str
        Email of the kid being added

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

    if not user.isParent:
        return json.dumps({'status': 0, 'error': "Access Denied"})

    kid_name = request_json['kid_name']
    kid_email = request_json['kid_email']

    random_password = ''.join(
        random.choices(
            string.digits + string.ascii_uppercase,
            k=8
        )
    )
    hashed_pwd = bcrypt.generate_password_hash(random_password).decode('utf-8')

    kid_user = User(
        name=kid_name,
        email=kid_email,
        password=hashed_pwd,
        isParent=False,
        accountId=user.accountId,
        parent_id=user.id
    )
    db.session.add(kid_user)
    db.session.commit()

    msg = Message('KidFin Login Credentials', sender='rachitbhargava99@gmail.com', recipients=[kid_user.email])
    msg.body = f'''Hi {kid_name},

You have been added by your parent to their account. You may now log in using the credentials listed below:

Username: {kid_email}
Password: {random_password}

Please be sure to keep this email secure.

Cheers,
KidFin Team'''
    mail.send(msg)

    return json.dumps({'status': 1, 'message': "Account Created Successfully!"})


@kid.route('/kid/add_restriction', methods=['POST'])
def add_kid_restriction():
    """Adds a new restriction to a kid account

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in
    User must be parent
    User must be parent of the kid whose ID is provided
    The provided Kid ID must be correct

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    amount: int         OPTIONAL
        Amount to limit each transaction to - defaults to UNLIMITED if nothing is provided
    transaction: int    OPTIONAL
        Maximum number of transactions allowed - defaults to UNLIMITED if nothing is provided
    address: str        OPTIONAL
        Address of the primary location
        Must not be more than 127 characters long
    distance: int       OPTIONAL
        Distance from the primary location where the transaction can be made - defaults to UNLIMITED
    kid_id: int
        Internal ID of kid whose account need the restrictions

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

    if not user.isParent:
        return json.dumps({'status': 0, 'error': "Access Denied"})

    amount = request_json.get('amount')
    transaction = request_json.get('transaction')
    address = request_json.get('address')
    distance = request_json.get('distance')
    kid_id = request_json['kid_id']

    kid_user = User.query.filter_by(id=kid_id).first()

    if kid_user is None:
        return json.dumps({'status': 0, 'error': "Invalid Kid ID"})

    if kid_user.parent_id != user.id:
        return json.dumps({'status': 0, 'error': "Kid is not linked to the logged in user"})

    new_restriction = Restriction(kid_id=kid_id)

    if bool(address) != bool(distance):
        return json.dumps({'status': 0,
                           'error': "Erroneous Request - Address and Distance must have values simultaneously"})

    if amount:
        new_restriction.amount = amount
    if transaction:
        new_restriction.transaction = transaction
    if address:
        new_restriction.primary_location = address
        new_restriction.distance = distance

    db.session.add(new_restriction)
    db.session.commit()

    return json.dumps({'status': 1})


@kid.route('/kid/remove_restriction', methods=['POST'])
def remove_kid_restriction():
    """Removes restriction from a kid account

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in
    User must be parent
    User must be parent of the kid whose ID is provided
    The provided Kid ID must be correct
    The provided Restriction ID must be correct

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    kid_id: int
        Internal ID of kid whose account need the restrictions
    restriction_id: int
        Internal Restriction ID of the restriction that needs to be removed

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

    if not user.isParent:
        return json.dumps({'status': 0, 'error': "Access Denied"})

    kid_id = request_json['kid_id']
    restriction_id = request_json['restriction_id']

    kid_user = User.query.filter_by(id=kid_id).first()

    if kid_user is None:
        return json.dumps({'status': 0, 'error': "Invalid Kid ID"})

    if kid_user.parent_id != user.id:
        return json.dumps({'status': 0, 'error': "Kid is not linked to the logged in user"})

    restriction = Restriction.query.filter_by(id=restriction_id).first()

    if restriction is None:
        return json.dumps({'status': 0, 'error': "Invalid Restriction ID"})

    restriction.isActive = False

    db.session.commit()

    return json.dumps({'status': 1})
