from urlparse import urlparse, urljoin
from flask import request, url_for, redirect
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    HiddenField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from models import User


"""
The following url checking is from:
Secure Back Redirects with WTForms
By Armin Ronacher

http://flask.pocoo.org/snippets/63/
"""


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_redirect_target():
    """This version will redirect to the referrer second.
    for target in request.args.get('next'), request.referrer:
        if not target:
            # print 'no target'
            continue
        if is_safe_url(target):
            # print 'safe target:', target
            return target
    """
    target = request.args.get('next')
    if not target:
        # print 'no target'
        return None
    if is_safe_url(target):
        # print 'safe target:', target
        return target


class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        # print 'checking ', self.next.data
        if is_safe_url(self.next.data):
            # print self.next.data, 'is ok'
            return redirect(self.next.data)
        target = get_redirect_target()
        # print 'redirecting to', target
        return redirect(target or url_for(endpoint, **values))
    """
    def redirect(self, endpoint='index', **values):
        print 'checking endpoint:', endpoint
        if is_safe_url(endpoint):
            print endpoint, 'is ok'
            return redirect(endpoint)

        print 'checking next.data:', self.next.data
        if is_safe_url(self.next.data):
            print self.next.data, 'is ok. redirecting'
            return redirect(self.next.data)

        target = get_redirect_target()
        print 'attempting to redirecting to default:', target

        return redirect(target or url_for(endpoint, **values))
    """


class LoginForm(RedirectForm):
    """
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    """
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already in use.')


class ParticipantForm(Form):
    username = StringField('Participant ID', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
