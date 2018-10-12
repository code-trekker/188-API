from sqlalchemy import desc, asc

from wmapp import *
from models import User, Tokens
import time

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])

            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/api/register', methods=['POST'])
@cross_origin('*')
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    exists = User.query.filter_by(username=data['username']).first()

    if exists is None:
        new_user = User(
            username=data['username'], 
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Registered successfully!'}), 200
    else:
        return jsonify({'message': 'User already exists!'}), 500


@app.route('/api/login', methods=['GET'])
@cross_origin('*')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    user = User.query.filter_by(username=auth.username).first()
    tokens = Tokens.query.filter_by(uid=user.id).first()
    print ('a')
    fmt = '%Y-%m-%d %H:%M:%S.%f %Z'

    if not user:
        print ('b')
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    if check_password_hash(user.password_hash, auth.password):
        print ('c')
        if tokens is None:
            print ('d')
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=4320)
            exp = exp.replace(tzinfo=pytz.utc)
            token = jwt.encode(
                {'username': user.username, 'exp': exp.astimezone(pytz.timezone("Asia/Singapore"))},
                app.config['SECRET_KEY'])
            utc_changed = datetime.datetime.utcnow() + datetime.timedelta(minutes=4320) + datetime.timedelta(hours=8)
            utc_changed = utc_changed.replace(tzinfo=pytz.utc)
            new_token = Tokens(uid=user.id, token=token,
                               ttl=utc_changed.astimezone(pytz.timezone("Asia/Singapore")))
            db.session.add(new_token)
            db.session.commit()

            return jsonify(
                {
                    'status': 200, 
                    'token': token.decode('UTF-8'), 
                    'user_id': user.id,
                    'username': user.username,
                    'message': 'Login successful!'
                }
            )

        else:
            print ('e')
            diff1 = tokens.ttl
            diff2 = datetime.datetime.utcnow()
            diff2 = diff2.replace(tzinfo=pytz.utc)
            diff = diff1 - (diff2.astimezone(pytz.timezone("Asia/Singapore")))
            minutessince = int(diff.total_seconds() / 60)

            if (minutessince > 0):
                expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutessince)
                expiry = expiry.replace(tzinfo=pytz.utc)
                token = jwt.encode(
                    {'username': user.username, 'exp': expiry.astimezone(pytz.timezone("Asia/Singapore"))},
                    app.config['SECRET_KEY'])

                return jsonify(
                    {
                        'status': 200,
                        'username': user.username,
                        'user_id': user.id, 
                        'token': token.decode('UTF-8'),
                        'message': 'Login successful!',
                    }
                )

            elif (minutessince <= 0):

                tokened = jwt.encode(
                    {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=4320)+ datetime.timedelta(hours=8)},
                    app.config['SECRET_KEY'])

                updated = Tokens.query.filter_by(uid=user.id).first()
                updated.token = tokened
                utc = datetime.datetime.utcnow() + datetime.timedelta(minutes=4320) + datetime.timedelta(hours=8)
                utc = utc.replace(tzinfo=pytz.utc)
                updated.ttl = (utc.astimezone(pytz.timezone("Asia/Singapore")))
                db.session.commit()

                return jsonify(
                    {
                        'status': 200,
                        'username': user.username,
                        'user_id': user.id, 
                        'token': tokened.decode('UTF-8'),
                        'message': 'Login successful!',
                    }
                )

@app.route('/api/exercises', methods=['GET'])
@cross_origin('*')
@token_required
def exercises():
    pass

@app.route('/api/add_exercise', methods=['POST'])
@cross_origin('*')
@token_required
def add_exercise():
    pass

@app.route('/api/edit_exercise', methods=['POST'])
@cross_origin('*')
@token_required
def edit_exercise():
    pass

@app.route('/api/remove_exercise', methods=['POST'])
@cross_origin('*')
@token_required
def remove_exercise():
    pass