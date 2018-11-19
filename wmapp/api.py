from sqlalchemy import desc, asc

from wmapp import *
from models import User, Tokens, Exercise, Routine, Workout, Profile, Weight
import datetime

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

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

    print auth
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
        token = jwt.encode({'user_id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])

        return jsonify({
            'status' : 200,
            'token' : token.decode('UTF-8'),
            'user_id' : user.id,
            'message': "Logged in successfully!"
        })
    
    else:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})


@app.route('/api/exercises', methods=['POST'])
@cross_origin('*')
# @token_required
def exercises():
    data = request.get_json()
    res = []

    exes = Exercise.query.filter_by(uid=int(data["user_id"]),is_deleted=False).order_by(desc(Exercise.eid)).all()
    
    for ex in exes:
        user_exercises = {}
        user_exercises["eid"] = ex.eid
        user_exercises["name"] = ex.name
        user_exercises["category"] = ex.category
        user_exercises["primary_muscle"] = ex.primary_muscle
        user_exercises["secondary_muscle"] = ex.secondary_muscle
        user_exercises["equipment"] = ex.equipment
        res.append(user_exercises)


    return jsonify({
        'status' : 200,
        'exercises' : res,
        'count' : len(res)
    })

@app.route('/api/add_exercise', methods=['POST'])
@cross_origin('*')
# @token_required
def add_exercise():
    data = request.get_json()
    
    new_exercise = Exercise(uid=data['user_id'], name=data['name'], category=data['category'], 
                            primary_muscle=data['primary_muscle'], secondary_muscle=data['secondary_muscle'], 
                            equipment=data['equipment'])

    db.session.add(new_exercise)
    db.session.commit()

    return jsonify({
        'message' : 'Exercise added successfully!',
        'status' : 200
    })


@app.route('/api/edit_exercise', methods=['POST'])
@cross_origin('*')
# @token_required
def edit_exercise():
    data = request.get_json()

    to_edit = Exercise.query.filter_by(eid=data['eid']).first()

    to_edit.name = data['name']
    to_edit.category = data['category']
    to_edit.primary_muscle = data['primary_muscle']
    to_edit.secondary_muscle = data['secondary_muscle']
    to_edit.equipment = data['equipment']

    db.session.commit()
    
    return jsonify({
        "status" : 200,
        "message" : "Edited successfully!"
    })

@app.route('/api/remove_exercise', methods=['POST'])
@cross_origin('*')
# @token_required
def remove_exercise():
    data = request.get_json()

    to_remove = Exercise.query.filter_by(eid=data['eid']).first()

    to_remove.is_deleted = True
    
    db.session.commit()
    
    return jsonify({
        "status" : 200,
        "message" : "Removed successfully!"
    })

@app.route('/api/routines', methods=['POST'])
@cross_origin('*')
def routines():
    data = request.get_json()
    res = []

    routs = Routine.query.filter_by(uid=data["user_id"], is_deleted=False).order_by(desc(Routine.rid)).all()

    print len(routs)

    for rout in routs:
        user_routines = {}
        user_routines["rid"] = rout.rid
        user_routines["name"] = rout.name
        user_routines["muscle_area"] = rout.muscle_area
        user_routines["eid"] = rout.eid
        ex_list = []

        for ex in rout.eid:
            searched = Exercise.query.filter_by(eid=ex).first()
            ex_list.append(searched.name)

        user_routines["exercise_list"] = ", ".join(ex_list)
        res.append(user_routines)
    
    return jsonify({
        'status' : 200,
        'routines' : res,
        'count' : len(res),
    })

@app.route('/api/add_routine', methods=['POST'])
@cross_origin('*')
def add_routine():
    data = request.get_json()

    new_routine = Routine(uid=data['user_id'], name=data['name'], eid=data['exercise_list'], muscle_area=data['muscle_area'])

    db.session.add(new_routine)
    db.session.commit()


    # if data['exercise_list'] == "":
    #     pass
    # else:
    #     for entry in data['exercise_list']:
    #         new_routine_exercise = RoutineExercise(rid=new_routine.rid, eid=entry)
    #         db.session.add(new_routine_exercise)
    #         db.session.commit()  

    return jsonify({
        'message' : 'Routine added successfully!',
        'status' : 200,
        'rid' : new_routine.rid
    })

# @app.route('/api/edit_routine_helper', methods=['POST'])
# @cross_origin('*')
# def edit_helper():
#     data = request.get_json

#     searched = Exercise.query.filter_by(rid=data["rid"]) 

#     res = []

#     for entry in searched:
#         result = {}
#         result["eid"] = entry.eid.eid
#         result["name"] = entry.eid.name
#         res.append(result)
    
#     return jsonify({
#         'message' : 'Routine added successfully!',
#         'results' : res,
#         'status' : 200
#     })

# @app.route('/api/edit_routine', methods=['POST'])
# @cross_origin('*')
# def edit_routine():
#     data = request.get_json()

#     pass

@app.route('/api/remove_routine', methods=['POST'])
@cross_origin('*')
def remove_routine():
    data = request.get_json()

    to_remove = Routine.query.filter_by(rid=data['rid']).first()

    to_remove.is_deleted = True
    
    db.session.commit()
    
    return jsonify({
        "status" : 200,
        "message" : "Removed successfully!"
    })

@app.route('/api/workouts', methods=['POST'])
@cross_origin('*')
def workouts():
    data = request.get_json()
    res = []

    workouts = Workout.query.filter_by(uid=int(data["user_id"]),is_deleted=False).order_by(desc(Workout.wid)).all()
    
    for work in workouts:
        user_workouts = {}
        user_workouts["wid"] = work.wid
        user_workouts["uid"] = work.uid
        search_routine = Routine.query.filter_by(rid=work.rid).first()
        user_workouts["rid"] = work.rid
        user_workouts["routine"] = search_routine.name
        t = work.day
        user_workouts["day"] = t.strftime("%a, %d %b %Y")
        user_workouts["notes"] = work.notes
       
        res.append(user_workouts)


    return jsonify({
        'status' : 200,
        'workouts' : res,
        'count' : len(res)
    })

@app.route('/api/add_workout', methods=['POST'])
@cross_origin('*')
def add_workout():
    data = request.get_json()

    new_workout = Workout(uid=data['user_id'], rid=data['rid'], notes=data['notes'], day=data['day'])

    db.session.add(new_workout)
    db.session.commit()  

    return jsonify({
        'message' : 'Workout added successfully!',
        'status' : 200,
    })

@app.route('/api/remove_workout', methods=['POST'])
@cross_origin('*')
def remove_workout():
    data = request.get_json()

    to_remove = Workout.query.filter_by(wid=data['wid']).first()

    to_remove.is_deleted = True
    
    db.session.commit()
    
    return jsonify({
        "status" : 200,
        "message" : "Removed successfully!"
    })


@app.route('/api/profile', methods=['POST'])
@cross_origin('*')
def profile():
    data = request.get_json()
    res = []

    profiles = Profile.query.filter_by(uid=int(data["user_id"])).first()
    
    if profiles is None:
        user_profile = {}
        user_profile["uid"] = None
        user_profile["first_name"] = None
        user_profile["last_name"] = None
        user_profile["lifestyle_type"] = None
        user_profile["birthday"] = None
        user_profile["gender"] = None
        user_profile["workout_aim"] = None
        user_profile["weight"] = None
        user_profile["height"] = None
        res.append(user_profile)

        return jsonify({
            'status' : 200,
            'profile' : res,
            'pid': None
        })

    else:
        user_profile = {}
        user_profile["uid"] = profiles.uid
        user_profile["first_name"] = profiles.first_name
        user_profile["last_name"] = profiles.last_name
        user_profile["lifestyle_type"] = profiles.lifestyle_type
        user_profile["birthday"] = str(profiles.birthday)
        user_profile["gender"] = profiles.gender
        user_profile["workout_aim"] = profiles.workout_aim
        user_profile["weight"] = str(profiles.weight)
        user_profile["height"] = str(profiles.height)
        res.append(user_profile)

        return jsonify({
            'status' : 200,
            'profile' : res,
            'pid' : profiles.pid
        })

@app.route('/api/edit_profile', methods=['POST'])
@cross_origin('*')
def edit_profile():
    data = request.get_json()

    # prof = Profile.query.filter_by(pid=data['pid']).first()

    if data["pid"] == "":
        new_prof = Profile(uid=data['user_id'], lifestyle_type=data["lifestyle_type"], birthday=data["birthday"], 
                            gender=data["gender"], workout_aim=data["workout_aim"], weight=data["weight"], height=data["height"],
                            first_name=data["first_name"], last_name=data["last_name"])

        db.session.add(new_prof)
        db.session.commit()
        
        return jsonify({
            "status" : 200,
            "message" : "Edited successfully!"
        })
    
    else:
        to_edit = Profile.query.filter_by(pid=data['pid']).first()

        to_edit.first_name = data['first_name']
        to_edit.last_name = data['last_name']
        to_edit.lifestyle_type = data['lifestyle_type']
        to_edit.birthday = data['birthday']
        to_edit.gender = data['gender']
        to_edit.workout_aim = data['workout_aim']
        to_edit.weight = data['weight']
        to_edit.height = data['height']

        db.session.commit()
        
        return jsonify({
            "status" : 200,
            "message" : "Edited successfully!"
        })


@app.route('/api/weight', methods=['POST'])
@cross_origin('*')
def weight():
    data = request.get_json()
    res = []
    
    weights = Weight.query.filter_by(weid=int(data['user_id']), is_deleted=False).order_by(desc(Weight.weid)).all()

    pass

@app.route('/api/add_weight', methods=['POST'])
@cross_origin('*')
def add_weight():
    pass

@app.route('/api/remove_weight', methods=['POST'])
@cross_origin('*')
def remove_weight():
    pass

@app.route('/api/weight_chart', methods=['POST'])
@cross_origin('*')
def weight_chart():
    pass