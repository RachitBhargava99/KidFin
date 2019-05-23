from flask import Blueprint, request, current_app
from backend.models import User
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
