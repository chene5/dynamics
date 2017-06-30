"""
Routes and views for the flask application.
"""
from datetime import datetime
import os.path
from json import dumps

from flask import render_template, redirect, request, session, make_response, \
    url_for
from flask.ext.login import login_user, logout_user, login_required, \
    current_user

from application import application, db
from models import User, Role
from forms import LoginForm, RegistrationForm, ParticipantForm

import thoughtslib
import researchlib
import studylib
import utilslib
import eec_utils
import processtweets

# refers to application_top
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

FLOW_WORDS_LENGTH = 10

FEEDBACK_PREFIX = "feedback"
FULL_PROMPT_PREFIX = "full_prompt"
NO_PROMPT_PREFIX = "no_prompt"

USER_HEADER = ['Username', 'User ID', 'rid', 'RISN', 'Condition', 'Role']


@application.route('/index')
def index():
    return redirect('/')


@application.route('/')
@application.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home',
        username=get_username().title(),
        year=datetime.now().year)


@application.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        username=get_username().title(),
        title='About Forward Flow',
        year=datetime.now().year
    )


@application.route('/forward_flow', methods=['GET', 'POST'])
def forward_flow():
    """Renders the Flow page."""
    if not current_user.is_authenticated:
        # Just create a new participant if the current user isn't logged in.
        username = create_participant()
        print 'flow(): New participant {} registered & logged in'.format(
            username)
    user_id = current_user.get_id()

    if request.method == 'POST':
        # This is for testing.
        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)
            # output = thoughtslib.save_word_list()
            # print output
            return redirect(url_for('graph'))

    # Get a new seed word.
    thoughtslib.get_set_seed_word()

    output, old_word, user_words, word_count = thoughtslib.start_flow()

    list_length = FLOW_WORDS_LENGTH
    username = get_username()

    return render_template(
        'forward_flow.html',
        title='Free associate',
        year=datetime.now().year,
        output=output,
        old_word=old_word,
        word_list=list(reversed(user_words[:-1])),
        word_count=word_count,
        list_length=list_length,
        username=username.title()
    )


@application.route('/graph', methods=('GET', 'POST'))
def graph():
    """
    Renders the graph page.
    """
    title = 'Thought Plot'
    # header = None
    if not current_user.is_authenticated:
        # Just create a new participant if the current user isn't logged in.
        username = create_participant()
        print 'graph(): New participant {} registered & logged in'.format(
            username)
    user_id = current_user.get_id()
    if request.method == 'POST':
        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

    list_length = FLOW_WORDS_LENGTH

    flow_and_words = studylib.get_flow_and_words(user_id, list_length)
    flow_data = flow_and_words[0]
    words = flow_and_words[1]
    average = flow_and_words[2]
    # print len(flow_data)
    # print len(words)
    if average:
        message = "Forward Flow: " + str(round(average,3))
    else:
        message = "Please enter more words"
    return render_template(
        'graph.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=title,
        message=message,
        flow_data=flow_data,
        average=average,
        words=words)


@application.route('/query_data', methods=['GET', 'POST'])
def query_data():
    """
    Renders the query data page, which has extra functionality
    for querying lists.
    """
    if request.method == 'POST':
        if 'download' in request.form:
            word_list, output = thoughtslib.construct_do_list()
            csv_str = make_csv_str(word_list, output)
            # print 'csv_str:', csv_str
            response = make_response(csv_str)
            curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = 'results_' + curr_time + '.csv'
            # print 'filename:', filename
            response.headers["Content-Disposition"] = \
                "attachment; filename=" + filename
            response.mimetype = 'text/csv'
            return response
        elif 'explore' in request.form:
            # word_list, table, average = thoughtslib.construct_do_list()
            word_list, table, average = studylib.analyze_form_word_list()
            try:
                average = round(average, 3)
            except TypeError:
                average = None
            except:
                raise
            message = 'Forward Flow: ' + str(average)
            # Display the results on the page.
            return render_template(
                'query_data.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='Analyze data',
                message=message,
                word_list=word_list,
                output=table
            )
        elif 'analyzeWordsFileBasic' in request.form:
            # print "Analysis file sent"
            return researchlib.do_research()
        elif 'analyzeFileDist' in request.form:
            # print "Analysis file sent"
            return researchlib.do_research()
        elif 'analyzeFileSummary' in request.form:
            # print "Analysis file sent"
            return researchlib.do_research()
        elif 'analyzeFileSerial' in request.form:
            # print "Analysis file sent"
            return researchlib.do_research()
        else:
            # Unknown POST request..
            return render_template(
                'query_data.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='Analyze data',
                message='Unknown request'
            )
    else:
        return render_template(
            'query_data.html',
            year=datetime.now().year,
            username=get_username().title(),
            title='Analyze data',
            message='Enter a list or upload a file',
        )


@application.route('/upload_data', methods=('GET', 'POST'))
def upload_data():
    # print 'upload()'
    if request.method == 'GET':
        return redirect('/query_data')
    if not request.files:
        return render_template(
            'query_data.html',
            year=datetime.now().year,
            username=get_username().title(),
            title='Analyze data',
            message='No file was uploaded',
        )

    for infilename, infile in request.files.iteritems():
        if not infile:
            return render_template(
                'query_data.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='Analyze data',
                message='No file was uploaded',
                )

    file_contents = infile.stream.read().decode("utf-8")
    # print 'file_contents:', file_contents

    word_list, output = thoughtslib.construct_do_list(file_contents)
    # print 'output:', output
    csv_str = make_csv_str(word_list, output)
    # print 'csv_str:', csv_str
    response = make_response(csv_str)
    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = 'results_' + curr_time + '.csv'
    # print 'filename:', filename
    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'

    return response


@application.route('/team')
def team():
    """Renders the about page."""
    message = get_about_message()

    return render_template(
        'team.html',
        username=get_username().title(),
        title='Under the hood',
        year=datetime.now().year,
        message=message
    )


@application.route('/admin', methods=('GET', 'POST'))
def admin():
    """
    Renders the Admin page.
    """
    # print 'Admin page!'
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies
    """
    title = 'Admin page'
    message = "Welcome, adminstrator"
    if request.method == 'POST':
        if 'dataCount' in request.form:
            data_count = int(request.form['dataCount'])
        else:
            data_count = None
        if 'downloadData' in request.form:
            header, output = studylib.get_all_data()
            return utilslib.make_tsv([header] + output)
        elif 'downloadLatest' in request.form:
            header, output = studylib.get_all_data(last_count=data_count)
            return utilslib.make_tsv([header] + output)
        elif 'showLatestAnswers' in request.form:
            pass
        elif 'showAnswers' in request.form:
            header, output = studylib.get_answers()
            message = 'Here are the answers.'
            return render_template(
                'admin.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=title,
                message=message,
                header=header,
                output=output)
        elif 'showUsers' in request.form:
            header = USER_HEADER
            output = []
            for user in User.query.all():
                role = Role.query.filter_by(id=user.role_id).first()
                output.append([user.username,
                               user.id,
                               user.rid,
                               user.RISN,
                               user.condition,
                               role.name])
            message = 'Here are the users.'
            return render_template(
                'admin.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=title,
                message=message,
                header=header,
                output=output)
        elif 'showLatestUsers' in request.form:
            header = USER_HEADER
            output = []
            if not data_count:
                data_count = 1
            for user in User.query.order_by(User.id.desc()).limit(data_count):
                role = Role.query.filter_by(id=user.role_id).first()
                output.append([user.username,
                               user.id,
                               user.rid,
                               user.RISN,
                               user.condition,
                               role.name])
            message = 'Here are the users.'
            return render_template(
                'admin.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=title,
                message=message,
                header=header,
                output=output)
        elif 'showSequences' in request.form:
            header, output = studylib.get_sequences()
            message = 'Here are the sequences.'
            return render_template(
                'admin.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=title,
                message=message,
                header=header,
                output=output)
        elif 'downloadSequences' in request.form:
            header, output = studylib.get_sequences()
            return utilslib.make_tsv([header] + output)
        elif 'downloadAnswers' in request.form:
            header, output = studylib.get_answers()
            return utilslib.make_tsv([header] + output)
        """These are for debugging.
        elif 'loadS3Cons' in request.form:
            thoughtslib.add_s3_constructs()
            message = 'S3 constructs loaded!'
            return render_template(
                'admin.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=title,
                message=message)
        elif 'clearSequences' in request.form:
            studylib.clear_sequences()
            message = 'Sequences were cleared.'
        elif 'clearAnswers' in request.form:
            studylib.clear_answers()
            message = 'Answers were cleared.'
        elif 'clearUsers' in request.form:
            for user in User.query.all():
                if user.username == 'eric' or \
                        user.username == 'kurt' or \
                        user.username == 'jm':
                    continue
                db.session.delete(user)
                db.session.commit()
            message = 'Other users were cleared.'
        """
    return render_template(
        'admin.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=title,
        message=message)


@application.route('/run')
def run():
    """Start for non-actors"""
    title = 'Begin study'
    if not current_user.is_authenticated:
        username = create_participant(prefix='nonactor')
    else:
        username = get_username()
    return render_template(
        'study_start.html',
        year=datetime.now().year,
        username=username.title(),
        title=title,
    )


@application.route('/go')
def go():
    """Start for actors"""
    title = 'Begin study'
    if not current_user.is_authenticated:
        username = create_participant(prefix='actor')
    else:
        username = get_username()
    return render_template(
        'study_start.html',
        year=datetime.now().year,
        username=username.title(),
        title=title,
    )


@application.route('/run_study')
def run_study():
    """Start for actors"""
    title = 'Begin study'
    if not current_user.is_authenticated:
        username = create_participant(prefix=FEEDBACK_PREFIX)
    else:
        username = get_username()
    return render_template(
        'study_start_feedback.html',
        year=datetime.now().year,
        username=username.title(),
        title=title,
    )


@application.route('/study', methods=['GET'])
@application.route('/start', methods=['GET'])
def study():
    # print 'Study start page!'
    title = 'Begin study'
    rid = None
    RISN = None
    if request.method == 'GET':
        if 'rid' in request.args or 'RISN' in request.args:
            if 'rid' in request.args:
                rid = request.args.get('rid')
            if 'RISN' in request.args:
                RISN = request.args.get('RISN')
            if not current_user.is_authenticated:
                # For the Qualtrics study, create the participant here.
                username = create_participant(rid=rid, RISN=RISN)
                print 'study(): New participant {} registered & logged in'.\
                    format(username)
    return render_template(
        'study_start.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=title,
    )


def create_participant(prefix=None, rid=None, RISN=None):
    """
    if rid or RISN:
        print 'RISN is', RISN
        print 'rid is', rid
    """
    username = utilslib.make_partic_id(prefix)
    # print 'Adding participant', username
    user = User(username=username, rid=rid, RISN=RISN)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return username


@application.route('/irb', methods=['GET', 'POST'])
def irb():
    """Renders the study IRB page."""
    username = get_username()
    if request.method == 'POST':
        # print 'participant {} submitted'.format(form.username.data)
        if 'startStudy' in request.form:
            if not current_user.is_authenticated:
                username = create_participant()
                # print 'irb(): participant {} registered & logged in'.format(
                #     username)
            # XXX: TODO: Fix sequence for starting studies.
            # Run Feedback study.
            return redirect(url_for('associate'))
        else:
            print 'Unknown POST request'
    return render_template(
        'study_irb.html',
        title='Consent',
        year=datetime.now().year,
        username=username.title(),
        seed_word=thoughtslib.get_seed_word()
    )


@application.route('/intro')
def intro():
    """Renders the intro page."""
    if not current_user.is_authenticated:
        # This shouldn't happen, but don't just fail if it does.
        # output = "User isn't logged in!"
        username = create_participant()
        print 'intro(): New participant {} registered & logged in'.format(
            username)
    user_id = current_user.get_id()
    # print 'user_id:', user_id
    username = get_username()

    return render_template(
        'study_intro.html',
        title='Introduction',
        year=datetime.now().year,
        username=username.title(),
        seed_word=thoughtslib.get_seed_word(user_id)
    )


@application.route('/flow', methods=['GET', 'POST'])
def flow():
    """Renders the Flow page."""
    if not current_user.is_authenticated:
        # Just create a new participant if the current user isn't logged in.
        username = create_participant()
        print 'flow(): New participant {} registered & logged in'.format(
            username)

    if request.method == 'POST':
        # This is for testing.
        if 'continueBtn' in request.form:
            output = thoughtslib.save_word_list()
            # print output
            return redirect(url_for('uses'))

    output, old_word, user_words, word_count = thoughtslib.start_flow()

    # list_length = FLOW_WORDS_LENGTH
    list_length = thoughtslib.WORD_MAX_COUNT
    username = get_username()

    return render_template(
        'study_flow.html',
        title='Free associate',
        year=datetime.now().year,
        output=output,
        old_word=old_word,
        word_list=list(reversed(user_words[:-1])),
        word_count=word_count,
        list_length=list_length,
        username=username.title()
    )


@application.route('/creativity', methods=['GET', 'POST'])
def creativity():
    survey_title = 'Creativity'
    bottle = []
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'creat(): New participant {} registered & logged in'.format(
                username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_creativity.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/uses', methods=['GET', 'POST'])
def uses():
    survey_title = 'Uses'
    bottle = []
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'uses(): New participant {} registered & logged in'.format(
                username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_uses.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/slogans', methods=['GET', 'POST'])
def slogans():
    survey_title = 'Slogans'
    bottle = []
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'uses(): New participant {} registered & logged in'.format(
                username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_slogans.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/charity', methods=['GET', 'POST'])
def charity():
    survey_title = 'Charity'
    bottle = []
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'uses(): New participant {} registered & logged in'.format(
                username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'ideas' in request.form:
            studylib.save_answers(user_id)
            output = dumps({'return_val': '1'})
            return output

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_charity.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/captions', methods=['GET', 'POST'])
def captions():
    survey_title = 'Captions'
    bottle = []
    # print 'Survey page!'
    if request.method == 'GET':
        # print "survey page sent a get!"
        pass
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'captions(): New participant {} registered & logged in'.\
                format(username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_captions.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/similarities', methods=['GET', 'POST'])
def similarities():
    survey_title = 'Similarities'
    bottle = []
    # print 'Survey page!'
    if request.method == 'GET':
        # print "survey page sent a get!"
        pass
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'similarities(): New participant {} registered & logged in'.\
                format(username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_similarities.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/raven', methods=['GET', 'POST'])
def raven():
    survey_title = 'Pictures'
    bottle = []
    # print 'Survey page!'
    if request.method == 'GET':
        # print "survey page sent a get!"
        pass
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'raven(): New participant {} registered & logged in'.\
                format(username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_raven.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/questions', methods=['GET', 'POST'])
def questions():
    survey_title = 'Questions'
    bottle = []
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'questions(): New participant {} registered & logged in'.\
                format(username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_questions.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
    )


@application.route('/survey', methods=['GET', 'POST'])
def survey():
    survey_title = 'Survey page'
    bottle = []
    # print 'Survey page!'
    if request.method == 'GET':
        # print "survey page sent a get!"
        pass
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'survey(): New participant {} registered & logged in'.\
                format(username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            print "Info submitted!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            studylib.save_answers(user_id)

    return render_template(
        'study_survey.html',
        year=datetime.now().year,
        username=get_username().title(),
        title=survey_title,
        bottle=bottle,
        races=studylib.RACES
    )


@application.route('/debrief', methods=['GET', 'POST'])
def debrief():
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies
    """
    survey_title = 'Debriefing'
    bottle = []

    # Get Qualtrics rid and RISN for the redirect.
    rid = None
    RISN = None
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        # print "user_id:", user_id
        user = User.query.filter_by(id=user_id).first()
        # print "username:", user.username
        # print "rid:", user.rid
        # print "RISN:", user.RISN
        rid = user.rid
        RISN = user.RISN

    if request.method == 'GET':
        # print "debrief page sent a get!"
        pass
    if request.method == 'POST':
        if not current_user.is_authenticated:
            # This shouldn't happen, but don't just fail if it does.
            # output = "User isn't logged in!"
            username = create_participant()
            print 'debrief(): New participant {} registered & logged in'.\
                format(username)
        user_id = current_user.get_id()
        # print 'user_id:', user_id

        # This was from a continue click on the previous page.
        if 'continueBtn' in request.form:
            studylib.save_answers(user_id)

        if 'submitInfoBtn' in request.form:
            bottle = ['<POSTed values:>']
            # print "survey page sent a post!"
            if 'name' in request.form:
                bottle.append("<Hi, {}!!!!>".format(request.form['name']))
            for arg in request.args:
                print arg
            for fthing in request.form:
                info = "<{} says: {}>".format(fthing, request.form[fthing])
                print info
                bottle.append(info)
            if current_user.is_authenticated:
                user_id = current_user.get_id()
                print 'user_id:', user_id
            else:
                print "User isn't logged in!"
                bottle = "User isn't logged in!"
                return render_template(
                    'study_debrief.html',
                    year=datetime.now().year,
                    username=get_username().title(),
                    title=survey_title,
                    rid=rid,
                    RISN=RISN,
                    bottle=bottle,
                )
            studylib.save_answers(user_id)

    return render_template('study_debrief.html',
                           year=datetime.now().year,
                           username=get_username().title(),
                           title="Debriefing",
                           rid=rid,
                           RISN=RISN,
                           bottle=bottle)


@application.route('/study_complete', methods=['GET', 'POST'])
def study_complete():
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies
    """
    survey_title = 'Survey page'
    bottle = []
    if request.method == 'GET':
        # print "survey page sent a get!"
        pass
    if request.method == 'POST':
        if 'continueBtn' in request.form:
            # XXX: Save info to db!
            return redirect('/study_complete')

        bottle = ['<POSTed values:>']
        # print "survey page sent a post!"
        if 'name' in request.form:
            bottle.append("<Hi, {}!!!!>".format(request.form['name']))
        for arg in request.args:
            print arg
        for fthing in request.form:
            info = "<{} says: {}>".format(fthing, request.form[fthing])
            print info
            bottle.append(info)
        if current_user.is_authenticated:
            user_id = current_user.get_id()
            print 'user_id:', user_id
        else:
            print "User isn't logged in!"
            bottle = "User isn't logged in!"
            return render_template(
                'study_survey.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=survey_title,
                bottle=bottle,
            )
        studylib.save_answers(user_id)
    return render_template('study_completed.html',
                           year=datetime.now().year,
                           username=get_username().title(),
                           title="Thanks for participating!",
                           bottle=bottle,
                           cover='static/assets/img/mountains.jpg')


def get_about_message():
    try:
        construct_name = session['construct']
        message = thoughtslib.ABOUT_MESSAGES[construct_name]
    except:
        # print 'session about message not found, using default'
        message = thoughtslib._about_message
    return message


@application.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        year=datetime.now().year,
        username=get_username().title(),
        title='Contact',
        message='Guilty parties:'
    )


@application.route('/upload', methods=('GET', 'POST'))
def upload():
    # print 'upload()'
    if request.method == 'GET':
        return redirect('/query')
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies
    print 'request.files:', request.files
    """
    if not request.files:
        return render_template(
            'list.html',
            year=datetime.now().year,
            username=get_username().title(),
            title='Query a list',
            message='No file was uploaded',
        )

    for infilename, infile in request.files.iteritems():
        if not infile:
            return render_template(
                'list.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='Query a list',
                message='No file was uploaded',
                )

    file_contents = infile.stream.read().decode("utf-8")
    # print 'file_contents:', file_contents

    word_list, output = thoughtslib.construct_do_list(file_contents)
    # print 'output:', output
    csv_str = make_csv_str(word_list, output)
    # print 'csv_str:', csv_str
    response = make_response(csv_str)
    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = 'results_' + curr_time + '.csv'
    # print 'filename:', filename
    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'

    return response


@application.route('/load')
def load():
    """
    Renders the load page, which allows users to load a new construct.
    """
    # constructs_dict = thoughtslib.display_constructs()
    constructs_dict = thoughtslib.CONSTRUCTS_INFO
    output = []
    for construct_num, construct_info in constructs_dict.iteritems():
        output.append(construct_info)

    if 'construct' in request.args:
        construct_name = request.args.get('construct')
        # print 'New construct requested:', construct_name
        if construct_name:
            thoughtslib.load_construct(construct_name)
            message = get_about_message()
            return render_template(
                'load.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='New construct loaded',
                output=output,
                message=message
            )
    else:
        message = get_about_message()
        return render_template(
            'load.html',
            year=datetime.now().year,
            username=get_username().title(),
            title='Load a new construct',
            output=output,
            message=message
        )


@application.route('/query', methods=['GET', 'POST'])
def query():
    """
    Renders the list page, which has extra functionality
    for querying lists.
    """
    if request.method == 'POST':
        # print 'querying()'
        """
        print 'request.form:', request.form
        print 'request.args:', request.args
        print 'request.values:', request.values
        print 'request.data:', request.data
        print 'request.cookies:', request.cookies
        """
        word_list, output = thoughtslib.construct_do_list()
        # print 'output:', output
        if 'download' in request.form:
            csv_str = make_csv_str(word_list, output)
            # print 'csv_str:', csv_str
            response = make_response(csv_str)
            curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = 'results_' + curr_time + '.csv'
            # print 'filename:', filename
            response.headers["Content-Disposition"] = \
                "attachment; filename=" + filename
            response.mimetype = 'text/csv'
            """It would be nice to also render a new template with the results.
            render_template(
                'query.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='List query results:',
                message='Enter another list of words, separated by a ' + \
                    'comma and/or a new line.',
                word_list=word_list,
                output=output
            )
            """
            return response
        else:
            return render_template(
                'query.html',
                year=datetime.now().year,
                username=get_username().title(),
                title='List query results:',
                message='Enter another list, or upload a file',
                word_list=word_list,
                output=output
            )
    else:
        return render_template(
            'query.html',
            year=datetime.now().year,
            username=get_username().title(),
            title='Query a list',
            message='Enter a list or upload a file',
        )


@application.route('/extras', methods=['GET', 'POST'])
def extras():
    # print 'Extra! Extra!'
    extras_title = 'Extras!'
    if request.method == 'GET':
        return render_template(
            'extras.html',
            year=datetime.now().year,
            username=get_username().title(),
            title=extras_title,
            message='Have fun!',
        )

    if request.method == 'POST':
        if 'average' in request.form:
            # print 'Get average'
            # print 'request.form:', request.form
            if request.form['avg_word'] == '':
                avg_word = thoughtslib.get_random_word()
                """
                return render_template(
                    'extras.html',
                    year=datetime.now().year,
                    username=get_username().title(),
                    title=extras_title,
                    message="You didn't input a word",
                )
                """
            else:
                avg_word = request.form['avg_word']
            output = thoughtslib.get_relatedness_average(avg_word)
            if output:
                message = 'The average similarity between {} and {} '.format(
                    avg_word, request.form['avg_samples'])
                message += 'randomly chosen other words is: {}'.format(
                    str(round(output, 4)))
            else:
                message = 'Sorry, unable to compute similarity for {}'.format(
                    avg_word)
            return render_template(
                'extras.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=extras_title,
                message=message,
            )
        elif 'closest' in request.form:
            # print 'Get closest'
            # print 'request.form:', request.form
            if request.form['close_word'] == '':
                close_word = thoughtslib.get_random_word()
                """
                return render_template(
                    'extras.html',
                    year=datetime.now().year,
                    username=get_username().title(),
                    title=extras_title,
                    message="You didn't input a word",
                )
                """
            else:
                close_word = request.form['close_word']
            output = thoughtslib.get_closest_words(close_word)
            if output:
                # print output
                message = 'Closest words to {} are:  '.format(close_word)
                for word in output:
                    # XXX: Hack to format Bag-of-Words words.
                    the_word = clean_bow_word(word[1])
                    message += "({}: {}),  ".format(the_word,
                                                    round(word[0], 3))
            else:
                message = 'Sorry, unable to compute similarities for {}'.\
                    format(close_word)
            """
            message = 'The dictionary has {} words in it!'.format(
                thoughtslib._thought_construct.dictionary_len)
            """
            return render_template(
                'extras.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=extras_title,
                message=message,
            )
        elif 'random' in request.form:
            # print 'Get random'
            # print 'request.form:', request.form
            similarity, word1, word2 = thoughtslib.compare_random()
            word1 = clean_bow_word(word1)
            word2 = clean_bow_word(word2)
            if similarity:
                message = 'Similarity between {} and {} is {}.'.format(
                    word1, word2, round(similarity, 3))
            else:
                message = \
                    'Sorry, unable to compute similarities for {} and {}'.\
                    format(word1, word2)
            return render_template(
                'extras.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=extras_title,
                message=message,
            )
        elif 'pair' in request.form:
            # print 'Query pair'
            # print 'request.form:', request.form
            similarity, word1, word2 = thoughtslib.compare_pair()
            word1 = clean_bow_word(word1)
            word2 = clean_bow_word(word2)
            if similarity:
                message = 'Similarity between {} and {} is {}.'.format(
                    word1, word2, round(similarity, 3))
            else:
                message = \
                    'Sorry, unable to compute similarities for {} and {}'.\
                    format(word1, word2)
            return render_template(
                'extras.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=extras_title,
                message=message,
            )


def clean_bow_word(word):
    if word.startswith('zzz_'):
        word = word.replace('zzz_', '')
        word = word.replace('_', ' ')
    return word


def get_username():
    """
    if current_user.is_authenticated:
        return current_user.username
    else:
        return 'Guest'
    """
    """
    try:
        username = session['username']
    except KeyError:
        # print 'username not set'
        username = 'Guest'
    return username
    """
    return current_user.username


def get_day():
    try:
        day = session['day']
    except KeyError:
        day = datetime.today().strftime('%Y%m%d')
        # print 'Today is', day
    return day


def make_csv_str(word_list=None, input_list=None):
    # print 'input_list:', input_list
    if word_list:
        csv_str = ','
        for word in word_list:
            csv_str += word + ','
        csv_str += '\n'
    else:
        csv_str = ''

    for row in input_list:
        for item in row:
            if item == '\n':
                continue
            csv_str += str(item) + ','
        csv_str += '\n'
    return csv_str


def get_daily_message():
    potd_data = thoughtslib.get_potd(get_day())
    if potd_data:
        msg_header = 'The pair of the day from {} is:'.format(potd_data[0])
        if current_user.is_authenticated:
            msg_text = "'{}' is to '{}' (similarity: {}) as '{}' is to '{}' \
                (similarity: {}).".\
                format(potd_data[1][1],
                       potd_data[1][2],
                       potd_data[1][0],
                       potd_data[2][1],
                       potd_data[2][2],
                       potd_data[2][0])
        else:
            msg_text = "'{}' is to '{}' as '{}' is to '{}'.".\
                format(potd_data[1][1],
                       potd_data[1][2],
                       potd_data[2][1],
                       potd_data[2][2])
    else:
        msg_header = 'Welcome!'
        msg_text = "Take a look around!"
    return msg_header, msg_text


@application.route('/research', methods=('GET', 'POST'))
def research():
    """
    Renders the research page, which has extra functionality
    for doing research.
    """
    # print 'Secret page!'
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies

        elif 'battleDrama' in request.form:
            return redirect('/research')
        elif 'battleField' in request.form:
            return redirect('/research')

    """
    title = 'Researcher page'
    message = "Researchers' secret page"
    header = None
    if request.method == 'POST':
        if 'resetPage' in request.form:
            return redirect('/research')
        elif 'getCreatThresh' in request.form:
            print "Get creativity threshold"
            return researchlib.do_research()
        elif 'setCreatThresh' in request.form:
            print "Set creativity threshold"
            return researchlib.do_research()
        elif 'upload' in request.form:
            # print "Input file sent"
            return researchlib.do_research()
        elif 'wordsFromFile' in request.form:
            # print "Words list file sent"
            return researchlib.do_research()
        elif 'processTweets' in request.form:
            return processtweets.process_this_dir()
        elif 'getTweetMatrices' in request.form:
            return processtweets.get_matrices_from_dir()
        elif 'analyzeWordsFile' in request.form:
            # print "Analysis file sent"
            return researchlib.do_research()
        else:
            message, output = researchlib.do_research()
            header = output[0]
            output = output[1:6]
            return render_template(
                'research.html',
                year=datetime.now().year,
                username=get_username().title(),
                title=title,
                message=message,
                header=header,
                output=output)
    return render_template(
        'research.html',
        year=datetime.now().year,
        username=get_username().title(),
        title='Researcher page',
        message=message)


def dir_list():
    file_list = eec_utils.list_type_in_dir(os.getcwd(), '.csv')
    # print "Checked", APP_ROOT
    output = []
    for filename in file_list:
        output.append([eec_utils.get_filename(filename), filename])
    # print output
    return output
    pass


@application.route('/thoughts')
def thoughts():
    """Renders the thoughts page."""
    username = get_username()
    output, old_word, word_list, word_count = thoughtslib.run_thoughts()
    # This used to be the message:
    # message='Test thoughts page.',
    return render_template(
        'thoughts.html',
        title='Test the analysis engine!',
        year=datetime.now().year,
        output=output,
        old_word=old_word,
        word_list=word_list,
        username=username.title()
    )


@application.route('/visualize')
@application.route('/visualize/<name>')
def visualize():
    message = 'This is the visualization page.'
    return render_template(
        'visualize.html',
        year=datetime.now().year,
        username=get_username().title(),
        title='Visualize',
        message=message)


@application.route('/flow_api/<word_list>')
def flow_api(word_list):
    words = word_list.strip().split(',')
    sim_matrix, word_list = studylib.calculate_all_past(words,
                                                        include_none=True,
                                                        distance=True)
    flow_list_str = thoughtslib.matrix_to_str([sim_matrix])
    flow_list_str = flow_list_str.rstrip(';')
    return flow_list_str


@application.route('/flow_api/')
@application.route('/flow_api')
def flow_api_none():
    return "NA"


@application.route('/signin', methods=['GET', 'POST'])
@application.route('/signin_page', methods=['GET', 'POST'])
def signin_page():
    form = LoginForm()
    if form.validate_on_submit():
        print 'Login attempt by {}'.format(form.username.data)
        user = User.query.filter_by(
            username=form.username.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # session['username'] = form.username.data
            print '{} logged in'.format(form.username.data)
            return form.redirect('index')
        # flash('Invalid username or password.')
        # print('Invalid username or password.')
    return render_template('signin.html',
                           username=get_username().title(),
                           year=datetime.now().year,
                           title='Sign in',
                           form=form)


@application.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # print 'New user submitted'
        user = User(email=form.email.data,
                    username=form.username.data.lower(),
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # print 'User registered'
        # token = user.generate_confirmation_token()
        # send_email(user.email, 'Confirm Your Account',
        #            'auth/email/confirm', user=user, token=token)
        # flash('A confirmation email has been sent to you by email.')
        # print('A confirmation email has been sent to you by email.')
        return redirect(url_for('signin'))
    return render_template('register.html',
                           username=get_username().title(),
                           year=datetime.now().year,
                           title='Register',
                           form=form)


@application.route('/signout')
@login_required
def signout():
    # print current_user.username + ' is signing out.'
    logout_user()
    thoughtslib.clear_user_words()
    # session.clear()
    """
    subheader = 'You have signed out.'
    msg_header, msg_text = get_daily_message()

    return render_template(
        'index.html',
        title='Home',
        username=get_username().title(),
        year=datetime.now().year,
        subheader=subheader,
        msg_header=msg_header,
        msg_text=msg_text)
    """
    return redirect('/')


@application.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        if 'signout' in request.form:
            # print current_user.username + ' is signing out.'
            logout_user()
            thoughtslib.clear_user_words()
            # session.clear()
            return redirect('/')
    return render_template(
        'signout.html',
        title='Sign out')


"""
@application.before_request
def before_request():
    g.user = current_user
"""


@application.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html',
                           year=datetime.now().year,
                           username=get_username().title(),
                           title="Sorry!",
                           message="The requested page couldn't be found.",
                           cover='/static/assets/img/mountains.jpg'), \
                               404


@application.errorhandler(403)
def no_access(error):
    """To handle 403 separately."""
    return render_template('page_not_found.html',
                           year=datetime.now().year,
                           username=get_username().title(),
                           title="Sorry!",
                           message="You don't have access to this page.",
                           cover='static/assets/img/mountains.jpg'), 403


@application.route('/associate', methods=['GET', 'POST'])
def associate():
    """Renders the free associate with feedback page."""
    if not current_user.is_authenticated:
        # Create the username with the proper prefix.
        username = create_participant(FEEDBACK_PREFIX)
        """
        if do_full_prompt:
            username = create_participant(FULL_PROMPT_PREFIX)
        else:
            username = create_participant(NO_PROMPT_PREFIX)
        """
        print 'associate(): New participant {} registered & logged in'.format(
            username)
    if request.method == 'POST':
        # This is for testing.
        if 'submitWords' in request.form:
            output = thoughtslib.flow_step()
            # print output
            return redirect('/')

    output, old_word, user_words, word_count = thoughtslib.start_flow()
    username = get_username()

    # Get the prompt condition.
    user_id = current_user.get_id()
    condition = utilslib.get_set_flow_condition(user_id)
    # condition = utilslib.calc_flow_condition()
    # print "condition:", condition
    if condition == utilslib.CONDITION_CONTROL:
        render_page = 'prompt_none_list.html'
    else:
        render_page = 'prompt_full_list.html'

    return render_template(
        render_page,
        title='Associate',
        year=datetime.now().year,
        output=output,
        old_word=old_word,
        word_list=list(reversed(user_words[:-1])),
        word_count=word_count,
        username=username.title()
    )


@application.route('/associate2', methods=['GET', 'POST'])
def associate2():
    """Renders the free associate with feedback page."""
    if not current_user.is_authenticated:
        # Create the username with the proper prefix.
        username = create_participant(FEEDBACK_PREFIX)
        """
        if do_full_prompt:
            username = create_participant(FULL_PROMPT_PREFIX)
        else:
            username = create_participant(NO_PROMPT_PREFIX)
        """
        print 'associate(): New participant {} registered & logged in'.format(
            username)
    if request.method == 'POST':
        # This is for testing.
        if 'submitWords' in request.form:
            output = thoughtslib.flow_step()
            # print output
            return redirect('/')

    output, old_word, user_words, word_count = thoughtslib.start_flow()
    username = get_username()

    # Get the prompt condition.
    user_id = current_user.get_id()
    condition = utilslib.get_set_flow_condition(user_id)
    # condition = utilslib.calc_flow_condition()
    # print "condition:", condition
    if condition == utilslib.CONDITION_CONTROL:
        render_page = 'prompt_none.html'
    else:
        render_page = 'prompt_full.html'

    return render_template(
        render_page,
        title='Associate',
        year=datetime.now().year,
        output=output,
        old_word=old_word,
        word_list=list(reversed(user_words[:-1])),
        word_count=word_count,
        username=username.title()
    )


@application.route('/study_login', methods=['GET', 'POST'])
def study_login():
    # print 'study login'
    header = "Please enter your participant information"
    form = ParticipantForm()
    # print form
    if request.method == 'POST':
        # print 'participant {} submitted'.format(form.username.data)
        if form.validate_on_submit():
            # print 'Participant validated'
            user = User(username=form.username.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            print 'participant {} registered & logged in'.format(
                form.username.data)
            return redirect(url_for('intro'))
        else:
            print 'form not valid'
            header = "Your participant information was invalid. \
                Please re-enter."
    return render_template('study_login.html',
                           username=get_username().title(),
                           year=datetime.now().year,
                           title='Register',
                           header=header,
                           form=form)


@application.route('/flow_dynamic', methods=['GET', 'POST'])
def flow_dynamic():
    """Renders the study flow page."""
    # word_list = user_words[1:]
    # This used to be the message:
    # message='Test thoughts page.',
    if not current_user.is_authenticated:
        # This shouldn't happen, but don't just fail if it does.
        # output = "User isn't logged in!"
        username = create_participant()
        print 'flow_dynamic(): New participant {} registered & logged in'.\
            format(username)

    if request.method == 'POST':
        # user_id = current_user.get_id()
        # print 'user_id:', user_id

        # This is for testing.
        if 'submitWords' in request.form:
            # output = thoughtslib.word_saver()
            output = thoughtslib.flow_step()
            # print output
            return redirect('/uses')

    # output, old_word, user_words, word_count = thoughtslib.run_thoughts()
    output, old_word, user_words, word_count = thoughtslib.start_flow()
    username = get_username()

    return render_template(
        'study_flow.html',
        title='Study',
        year=datetime.now().year,
        output=output,
        old_word=old_word,
        word_count=word_count,
        username=username.title()
    )


@application.route('/process_thoughts', methods=['GET', 'POST'])
def process_thoughts():
    # print 'process_thoughts()'
    # output = thoughtslib.word_recorder()
    output = thoughtslib.flow_step()
    if output:
        return output
    else:
        # XXX: There should always be an output
        # Letting the client browser handle when the max count is reached.
        #       return redirect('/uses')
        pass


@application.route('/done_process', methods=['GET', 'POST'])
def done_process():
    return redirect('/uses')


@application.route('/reset_thoughts', methods=['GET', 'POST'])
def reset_thoughts():
    # print 'reset_thoughts()'
    return thoughtslib.thought_reseter()


@application.route('/save_words', methods=['GET', 'POST'])
def save_words():
    # print 'save_words()'
    return thoughtslib.word_saver()


@application.route('/do_tweets', methods=['GET', 'POST'])
def do_tweets():
    output = processtweets.process_this_dir()
    return output


"""Uncomment this to initialize the admin user.
@application.route('/initialize')
def initialize():
    print 'Create Admin'
    user = User(email='admin@example.com',
                username='admin',
                password='aGeAVKg9')
    db.session.add(user)
    db.session.commit()
    return redirect('/signin')
"""
