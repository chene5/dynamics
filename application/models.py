"""
Models for the flask application.
"""
from datetime import datetime
# import hashlib
from flask import current_app, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.dialects.mysql import SMALLINT

from application import db, login_manager


class Permission:
    WRITE = 0x01
    PARTICIPATE = 0x02
    RESEARCH = 0X04
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(SMALLINT, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.WRITE, True),
            'Participant': (Permission.WRITE |
                            Permission.PARTICIPATE, False),
            'Researcher': (Permission.WRITE |
                           Permission.PARTICIPATE |
                           Permission.RESEARCH, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        # return '<Role %r>' % self.name
        return '<Role #{} {}>'.format(self.id, self.name)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(SMALLINT, default=False)
    name = db.Column(db.String(64))
    rid = db.Column(db.String(64))
    RISN = db.Column(db.String(64))
    condition = db.Column(db.String(64))

    # Word sequences
    sequences = db.relationship('Sequence', backref='user', lazy='dynamic')

    # Survey answers (e.g., demographics)
    answers = db.relationship('Answer', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.username == current_app.config['CREATIVE_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                print 'Welcome, {}'.format(
                    current_app.config['CREATIVE_ADMIN'])
            elif self.username == 'kurt':
                self.role = Role.query.filter_by(permissions=0x07).first()
                print 'Hi, {}'.format(self.username)
            elif self.username == 'jm':
                self.role = Role.query.filter_by(permissions=0x07).first()
                print 'Hi, {}'.format(self.username)
            elif self.username == 'stephen':
                self.role = Role.query.filter_by(permissions=0x07).first()
                print 'Hi, {}'.format(self.username)
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        # print self.role
        # print self.role.permissions
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'username': self.username,
            'sequences': url_for('api.get_user_sequences',
                                 id=self.id, _external=True),
            'sequence_count': self.sequences.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % (self.username)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def __init__(self):
        self.username = 'Guest'


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Participant(UserMixin, db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(SMALLINT, default=False)
    name = db.Column(db.String(64))

    # Word sequences
    sequences = db.relationship('Sequence',
                                backref='participant',
                                lazy='dynamic')

    # Survey answers (e.g., demographics)
    answers = db.relationship('Answer',
                              backref='participant',
                              lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        print "Creating user ", self.username
        if self.role is None:
            self.role = Role.query.filter_by(
                permissions=Permission.PARTICIPATE).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        # print self.role
        # print self.role.permissions
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return False

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'username': self.username,
            'sequences': url_for('api.get_user_sequences',
                                 id=self.id, _external=True),
            'sequence_count': self.sequences.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<Participant %r>' % (self.username)


class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))

    def to_json(self):
        json_sequence = {
            'body': self.body,
            'timestamp': self.timestamp,
            'username': url_for('api.get_user', id=self.user_id,
                                _external=True)
        }
        return json_sequence

    def __repr__(self):
        message = '<Sequence %r>' % (self.body)
        message += '   <User %r>' % (self.user_id)
        message += '   <Participant %r>' % (self.participant_id)
        # return '<Sequence %r>' % (self.body)
        return message


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    creat_imp = db.Column(db.Text)
    use_1 = db.Column(db.Text)
    use_2 = db.Column(db.Text)
    use_3 = db.Column(db.Text)
    slogan1 = db.Column(db.Text)
    slogan2 = db.Column(db.Text)
    slogan3 = db.Column(db.Text)
    idea1 = db.Column(db.Text)
    idea2 = db.Column(db.Text)
    idea3 = db.Column(db.Text)
    caption_1 = db.Column(db.Text)
    caption_2 = db.Column(db.Text)
    caption_3 = db.Column(db.Text)
    pair_1 = db.Column(db.Text)
    pair_2 = db.Column(db.Text)
    pair_3 = db.Column(db.Text)
    raven_1 = db.Column(db.Text)
    raven_2 = db.Column(db.Text)
    raven_3 = db.Column(db.Text)
    raven_4 = db.Column(db.Text)
    raven_5 = db.Column(db.Text)
    raven_6 = db.Column(db.Text)
    gre_1 = db.Column(db.Text)
    gre_2 = db.Column(db.Text)
    gre_3 = db.Column(db.Text)
    gender = db.Column(db.Text)
    ethnicity = db.Column(db.Text)
    race = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Text)
    worker_id = db.Column(db.Text)
    effort = db.Column(db.Text)
    experience = db.Column(db.Text)
    national_count = db.Column(db.Text)
    success_acting = db.Column(db.Text)
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))

    def to_json(self):
        json_sequence = {
            'gender': self.gender,
            'ethnicity': self.ethnicity,
            'race': self.race,
            'education': self.education,
            'age': self.age,
            'timestamp': self.timestamp,
            'username': url_for('api.get_user', id=self.user_id,
                                _external=True)
        }
        return json_sequence

    def __repr__(self):
        message = '<Answer %r>' % (self.timestamp)
        message += '   <User %r>' % (self.user_id)
        message += '   <Participant %r>' % (self.participant_id)
        return message
