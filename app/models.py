from app import db, bcrypt
from flask import current_app
from app.helpers import get_public_id

import jwt
from datetime import datetime, timedelta


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, nullable=True, unique=True)
    name = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    profile_photo = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.Text, nullable=True)

    deleted = db.Column(db.Boolean, default=False)

    is_doctor = db.Column(db.Boolean, default=False)
    is_admin  = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    reports = db.relationship('Report', order_by='Report.id',
                            backref='author', lazy=True)

    replies = db.relationship('Reply', order_by='Reply.id',
                            backref='author', lazy=True)

    def __init__(self, name, email, password, is_doctor):
        self.name  = name
        self.email = email
        self.password  = bcrypt.generate_password_hash(password).decode()
        self.is_doctor = is_doctor

    def set_public_id(self):
        """Sets a Public ID for User"""

        self.public_id = get_public_id(f"{self.id}_user")
        self.save()

    def set_password(self, password):
        """Hashes User password"""

        self.password = bcrypt.generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self, flag=0):
        """Returns Users data as JSON/Dictionary"""

        _dict = {}
        if not self.deleted:
            _dict = {
                "public_id": self.public_id,
                "name": self.name,
                "email": None,
                "bio": self.description,
                "profile_photo": self.profile_photo,
                "joined": self.created_at,
                "is_doctor": self.is_doctor,
            }

            if flag == 1:
                if self.is_doctor:
                    _replies = [r.to_dict() for r in self.replies if not r.deleted]
                    _dict["replies"] = _replies
                    _all_reports = [ r.to_dict() for r in Report.query.order_by(Report.id.desc()).all() ]
                    _dict["all_reports"] = _all_reports

                else:
                    _reports = [r.to_dict() for r in self.reports if not r.deleted]
                    _dict["reports"] = _reports

                _dict["email"]   = self.email

        return _dict

    def delete(self):
        """Deletes User"""

        self.deleted = True
        self.save()

    def save(self):
        """Save/Updates the database"""

        db.session.add(self)
        db.session.commit()

    def generate_token(self, minutes=40320):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=minutes),
                'iat': datetime.utcnow(),
                'sub': self.id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )

            if type(jwt_string) == bytes:
                jwt_string = jwt_string.decode()

            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""

        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, current_app.config.get(
                'SECRET_KEY'), algorithms=['HS256'])
            return True, payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return False, "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return False, "Invalid token. Please register or login"

        return False, "Invalid token. Please register or login"


class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, nullable=True, unique=True)
    title = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    has_replies = db.Column(db.Boolean, nullable=False, default=False)

    deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    replies = db.relationship('Reply', order_by='Reply.id',
                            backref='report', lazy=True)

    def __init__(self, title, content, user_id):
        self.user_id = user_id
        self.content = content
        self.title   = title

    def set_public_id(self):
        """Sets a Public ID for Link"""

        self.public_id = get_public_id(f"{self.id}_report")
        self.save()

    def to_dict(self):
        """Returns Link's data as JSON/Dictionary"""

        _dict = {}
        if not self.deleted:
            _replies = [ r.to_dict() for r in self.replies if r.deleted == False]

            _dict = {
                "public_id": self.public_id,
                "title": self.title,
                "content": self.content,
                "replies" : _replies,
                "created_at": self.created_at,
                "author"   : self.author.to_dict()
            }

        return _dict

    def delete(self):
        self.deleted = True
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

class Reply(db.Model):
    __tablename__ = 'reply'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, nullable=True, unique=True)
    report_id = db.Column(db.Integer, nullable=False)

    content = db.Column(db.Text, nullable=True)

    deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)

    def __init__(self, content, report_id, user_id):
        self.user_id = user_id
        self.content = content
        self.report_id = report_id

    def set_public_id(self):
        """Sets a Public ID for Link"""

        self.public_id = get_public_id(f"{self.id}_reply")
        self.save()

    def to_dict(self):
        """Returns Link's data as JSON/Dictionary"""

        _dict = {}
        if not self.deleted:
            _dict = {
                "public_id": self.public_id,
                "content": self.content,
                "created_at": self.created_at,
                "author"   : self.author.to_dict(),
                "replied": self.report.public_id
            }

        return _dict

    def delete(self):
        self.deleted = True
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()
