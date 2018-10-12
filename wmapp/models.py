from wmapp import *

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(32), unique=True,index=True)
    password_hash=db.Column(db.String(1000))
    
class Tokens(db.Model):
    __tablename__ = 'tokens'
    tid = db.Column(db.Integer(), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(220))
    ttl = db.Column(db.DateTime(timezone=True))

class Profile(db.Model):
    __tablename__ = 'profile'
    pid = db.Column(db.Integer(), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    lifestyle_type = db.Column(db.String(50), nullable=True)
    birthday = db.Column(db.DATE, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    workout_aim = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.DECIMAL, nullable=True)
    height = db.Column(db.DECIMAL, nullable=True)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    eid = db.Column(db.Integer(), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50))
    category = db.Column(db.String(50))
    primary_muscle = db.Column(db.String(80))
    secondary_muscle = db.Column(db.String(80))
    equipment = db.Column(db.String(50))

class Routine(db.Model):
    rid = db.Column(db.Integer(), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    eid = db.Column(db.Integer, db.ForeignKey('exercise.eid'))
    description = db.Column(db.String(225))
    muscle_area = db.Column(db.String(50))

class Workout(db.Model):
    wid = db.Column(db.Integer(), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    day = db.Column(db.DATE)
    notes = db.Column(db.String(225))

