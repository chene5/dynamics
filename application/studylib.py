# -*- coding: utf-8 -*-
"""studylib.py
Functions for handling study questions.

Created on Sat Nov 28 06:58:43 2015

@author: Eric
"""
from json import dumps, loads
from random import sample
from datetime import datetime
from collections import OrderedDict

from flask import request, session, Markup
from flask.ext.login import current_user

from application import db
from models import Answer, Sequence, User

from utilslib import make_anon_id
from thoughtslib import WORD_MAX_COUNT

# Participants will first see one of these words.
SEED_WORDS = set(['toaster',
                  'table',
                  'bear',
                  'snow',
                  'paper',
                  'candle'])

RACES = OrderedDict()
RACES['AI_AN'] = 'American Indian/Alaskan Native'
RACES['Asian'] = 'Asian'
RACES['Black'] = 'Black or African American'
RACES['NH_PI'] = 'Native Hawaiian or other Pacific Islander'
RACES['White'] = 'White'
RACES['Other'] = 'Other'

ALL_DATA_HEADER = ['User ID',
                   'Username',
                   'rid',
                   'Condition',
                   'Word list',
                   'Full data',
                   'Flow time',
                   'User ID',
                   'Use 1',
                   'Use 2',
                   'Use 3',
                   'Slogan1',
                   'Slogan2',
                   'Slogan3',
                   'Idea1',
                   'Idea2',
                   'Idea3',
                   'Caption 1',
                   'Caption 2',
                   'Caption 3',
                   'Similarity 1',
                   'Similarity 2',
                   'Similarity 3',
                   'Raven 1',
                   'Raven 2',
                   'Raven 3',
                   'Raven 4',
                   'Raven 5',
                   'Raven 6',
                   'GRE 1',
                   'GRE 2',
                   'GRE 3',
                   'Gender',
                   'Race',
                   'Ethnicity',
                   'Education',
                   'Age',
                   'Worker ID',
                   'Effort',
                   'Creativity Imp.',
                   'Acting Experience',
                   'Nat. press count',
                   'Success acting',
                   'Comments',
                   'Tasks time',
                   'Total time']


def save_answers(user_id):
    """Save POSTed answers."""
    # print 'request.form:', request.form

    # First, get or create the Answer db entry.
    entry = Answer.query.filter_by(user_id=user_id).first()
    if not entry:
        entry = Answer(user_id=user_id,
                       user=current_user._get_current_object(),
                       timestamp=datetime.utcnow())

    flow_word_list = []
    race = []
    # Actor experience
    experience = []
    for question, answer in request.form.iteritems():
        # print 'question', question
        # print 'answer', answer

        # This saves a list of flow words.
        if question.startswith('word'):
            if not flow_word_list:
                # Iterate through the entire form sequentially.
                for i in range(1, WORD_MAX_COUNT + 1):
                    entry_name = 'word' + str(i)
                    # print "Reading entry:", entry_name
                    if entry_name in request.form:
                        word = request.form[entry_name]
                        if word:
                            flow_word_list.append(word)
                            # print 'flow word:', word
                    else:
                        continue

        elif question.startswith('creat_imp'):
            entry.creat_imp = answer
            # print 'creat_imp', entry.creat_imp

        elif question.startswith('use_'):
            # These are the Uses items.
            if question.startswith('use_1'):
                entry.use_1 = answer
                # print 'use_1', answer
            elif question.startswith('use_2'):
                entry.use_2 = answer
                # print 'use_2', answer
            elif question.startswith('use_3'):
                entry.use_3 = answer
                # print 'use_3', answer

        elif question.startswith('slogan'):
            # These are the Slogans.
            if question.startswith('slogan1'):
                entry.slogan1 = answer
                # print 'slogan1:', answer
            elif question.startswith('slogan2'):
                entry.slogan2 = answer
                # print 'slogan2:', answer
            elif question.startswith('slogan3'):
                entry.slogan3 = answer
                # print 'slogan3:', answer

        elif question.startswith('idea'):
            # These are the charity Ideas.
            if question.startswith('idea1'):
                entry.idea1 = answer
                # print 'idea1:', answer
            elif question.startswith('idea2'):
                entry.idea2 = answer
                # print 'idea2:', answer
            elif question.startswith('idea3'):
                entry.idea3 = answer
                # print 'idea3:', answer

        elif question.startswith('caption_'):
            # These are the Caption items.
            if question.startswith('caption_1'):
                entry.caption_1 = answer
                # print 'caption_1', answer
            elif question.startswith('caption_2'):
                entry.caption_2 = answer
                # print 'caption_2', answer
            elif question.startswith('caption_3'):
                entry.caption_3 = answer
                # print 'caption_3', answer

        elif question.startswith('pair_'):
            # These are the Pair items.
            if question.startswith('pair_1'):
                entry.pair_1 = answer
                # print 'pair_1', answer
            elif question.startswith('pair_2'):
                entry.pair_2 = answer
                # print 'pair_2', answer
            elif question.startswith('pair_3'):
                entry.pair_3 = answer
                # print 'pair_3', answer

        elif question.startswith('raven_'):
            # These are the Raven's items.
            if question.startswith('raven_1'):
                entry.raven_1 = answer
                # print 'raven_1', answer
            elif question.startswith('raven_2'):
                entry.raven_2 = answer
                # print 'raven_2', answer
            elif question.startswith('raven_3'):
                entry.raven_3 = answer
                # print 'raven_3', answer
            elif question.startswith('raven_4'):
                entry.raven_4 = answer
                # print 'raven_4', answer
            elif question.startswith('raven_5'):
                entry.raven_5 = answer
                # print 'raven_5', answer
            elif question.startswith('raven_6'):
                entry.raven_6 = answer
                # print 'raven_6', answer

        elif question.startswith('gre_'):
            # These are the GRE items.
            if question.startswith('gre_1'):
                entry.gre_1 = answer
                # print 'gre_1', answer
            elif question.startswith('gre_2'):
                entry.gre_2 = answer
                # print 'gre_2', answer
            elif question.startswith('gre_3'):
                entry.gre_3 = answer
                # print 'gre_3', answer

        # These are the survey questions.
        elif question.startswith('gender'):
            entry.gender = answer
            # print 'gender', entry.gender
        elif question.startswith('ethnicity'):
            entry.ethnicity = answer
            # print 'ethnicity', entry.ethnicity
        elif question in RACES:
            race.append(question)
            # print 'race', race
        elif question.startswith('education'):
            entry.education = answer
            # print 'education', entry.education
        elif question.startswith('age'):
            entry.age = answer
            # print 'age', entry.age
        elif question.startswith('worker_id'):
            entry.worker_id = answer
            # print 'worker_id', entry.worker_id
        elif question.startswith('effort'):
            entry.effort = answer
            # print 'effort', entry.effort
        elif question.startswith('exp_'):
            experience.append(question)
            # print 'experience', experience
        elif question.startswith('national_count'):
            entry.national_count = answer
            # print 'national_count', entry.national_count
        elif question.startswith('success_acting'):
            entry.success_acting = answer
            # print 'success_acting', entry.success_acting
        elif question.startswith('comments'):
            entry.comments = answer
            # print 'comments', entry.comments
        # print

    if flow_word_list:
        save_word_list(flow_word_list)

    if race:
        entry.race = dumps(race)

    if experience:
        entry.experience = dumps(experience)

    entry.timestamp = datetime.utcnow()

    db.session.add(entry)
    db.session.commit()


def get_answers():
    """Return answers, with header.

    Queries db.
    Returns: header, a list of the questions.
             answers, list of lists: the entire set of answers.
    """
    header = ['User ID',
              'Username',
              'Use 1',
              'Use 2',
              'Use 3',
              'Slogan1',
              'Slogan2',
              'Slogan3',
              'Idea1',
              'Idea2',
              'Idea3',
              'Caption 1',
              'Caption 2',
              'Caption 3',
              'Similarity 1',
              'Similarity 2',
              'Similarity 3',
              'Raven 1',
              'Raven 2',
              'Raven 3',
              'Raven 4',
              'Raven 5',
              'Raven 6',
              'GRE 1',
              'GRE 2',
              'GRE 3',
              'Gender',
              'Race',
              'Ethnicity',
              'Education',
              'Age',
              'Worker ID',
              'Effort',
              'Creativity Imp.',
              'Acting Experience',
              'Nat. press count',
              'Success acting',
              'Comments',
              'Total time']
    answers = []
    for answer in Answer.query.all():
        user = User.query.filter_by(id=answer.user_id).first()
        answers.append([answer.user_id,
                        user.username,
                        answer.use_1,
                        answer.use_2,
                        answer.use_3,
                        answer.slogan1,
                        answer.slogan2,
                        answer.slogan3,
                        answer.idea1,
                        answer.idea2,
                        answer.idea3,
                        answer.caption_1,
                        answer.caption_2,
                        answer.caption_3,
                        answer.pair_1,
                        answer.pair_2,
                        answer.pair_3,
                        answer.raven_1,
                        answer.raven_2,
                        answer.raven_3,
                        answer.raven_4,
                        answer.raven_5,
                        answer.raven_6,
                        answer.gre_1,
                        answer.gre_2,
                        answer.gre_3,
                        answer.gender,
                        answer.race,
                        answer.ethnicity,
                        answer.education,
                        answer.age,
                        answer.worker_id,
                        answer.effort,
                        answer.creat_imp,
                        answer.experience,
                        answer.national_count,
                        answer.success_acting,
                        answer.comments,
                        get_total_time(user, answer)])
    return header, answers


def clear_answers():
    for answer in Answer.query.all():
        db.session.delete(answer)
        db.session.commit()


def get_sequences():
    """Return answers, with header.

    Queries db.
    Returns: header.
             sequences, list of word lists.
    """
    header = ['User ID',
              'Username',
              'rid',
              'Sequence ID',
              'Word list',
              'Full data',
              'Flow time']
    sequences = []
    for sequence in Sequence.query.all():
        user = User.query.filter_by(id=sequence.user_id).first()
        sequences.append([sequence.user_id,
                          user.username,
                          user.rid,
                          sequence.id,
                          sequence.body,
                          sequence.data,
                          get_flow_time(user, sequence)])
    return header, sequences


def clear_sequences():
    for sequence in Sequence.query.all():
        db.session.delete(sequence)
        db.session.commit()


def extract_answer_data(answer):
    answer_data = [answer.user_id,
                   answer.use_1,
                   answer.use_2,
                   answer.use_3,
                   answer.slogan1,
                   answer.slogan2,
                   answer.slogan3,
                   answer.idea1,
                   answer.idea2,
                   answer.idea3,
                   answer.caption_1,
                   answer.caption_2,
                   answer.caption_3,
                   answer.pair_1,
                   answer.pair_2,
                   answer.pair_3,
                   answer.raven_1,
                   answer.raven_2,
                   answer.raven_3,
                   answer.raven_4,
                   answer.raven_5,
                   answer.raven_6,
                   answer.gre_1,
                   answer.gre_2,
                   answer.gre_3,
                   answer.gender,
                   answer.race,
                   answer.ethnicity,
                   answer.education,
                   answer.age,
                   answer.worker_id,
                   answer.effort,
                   answer.creat_imp,
                   answer.experience,
                   answer.national_count,
                   answer.success_acting,
                   answer.comments]
    return answer_data


def extract_user_data(user):
    user_data = [user.id,
                 user.username,
                 user.rid,
                 user.condition]
    return user_data


def extract_sequence_data(sequence):
    if sequence:
        sequence_data = [sequence.body,
                         sequence.data]
    else:
        sequence_data = ['', '']
    return sequence_data


def gen_data_from_sequence(sequence):
    answer = Answer.query.filter_by(user_id=sequence.user_id).first()
    user = User.query.filter_by(id=sequence.user_id).first()
    current_data = extract_user_data(user)
    current_data += extract_sequence_data(sequence)
    current_data.append(get_flow_time(user, sequence))
    if answer:
        current_data += extract_answer_data(answer)
        current_data.append(get_tasks_time(sequence, answer))
        current_data.append(get_total_time(user, answer))
    return current_data


def get_all_data(last_count=None):
    """Return all data, with header.

    Queries db.
    Returns: header.
             all_data
    """
    print "get_all_data"
    all_data = []
    # sequence = Sequence.query.filter_by(user_id=user_id). \
    #     order_by(Sequence.id.desc()).first()
    if last_count:
        for sequence in Sequence.query.order_by(Sequence.id.desc()).limit(last_count):
            all_data.append(gen_data_from_sequence(sequence))
    else:
        for sequence in Sequence.query.all():
            all_data.append(gen_data_from_sequence(sequence))

    return ALL_DATA_HEADER, all_data


def start_flow():
    """Start forward flow recording."""
    # print 'start_flow()'
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        user_id = make_anon_id()

    user_sequence = get_sequence(user_id)
    user_words = loads(user_sequence.body)
    # Don't count the seed word.
    word_count = len(user_words) - 1
    last_word = user_words[-1]
    # print "Word count:", word_count
    # print "start_flow(): User words:", user_words
    if word_count == 0:
        output = Markup("<p>Starting word: </p> <p>{}</p>".format(last_word))
    else:
        # output = Markup("<p>Previous word </p> <p>{}</p>".format(last_word))
        output = Markup("<p>Your last word was: </p> <p>{}</p>".format(
            last_word))

    return output, last_word, user_words, word_count


def get_sequence(user_id):
    """
    Get this user's sequence from the database.
    If no sequence exists, create one.
    """
    sequence = Sequence.query.filter_by(user_id=user_id).first()
    if not sequence:
        user_sequence = [get_seed_word()]
        sequence = setup_db_sequence(user_sequence, user_id)
        # print "Created new sequence for", user_id, ":", user_sequence
    return sequence


def setup_db_sequence(user_words, user_id):
    sequence = Sequence(body=dumps(user_words),
                        data='',
                        user_id=user_id,
                        user=current_user._get_current_object(),
                        timestamp=datetime.utcnow())
    db.session.add(sequence)
    db.session.commit()
    set_sequence_id(sequence.id)
    return sequence


def get_seed_word(user_id=None):
    if user_id:
        user_sequence = get_sequence(user_id)
        user_words = loads(user_sequence.body)
        seed_word = user_words[0]
    else:
        seed_word = sample(SEED_WORDS, 1)[0]
    return seed_word


def set_sequence_id(sequence_id):
    session['sequence_id'] = sequence_id
    # print session['sequence_id']


def save_word_list(word_list):
    """Save a list of words to the db."""
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        user_id = make_anon_id()

    # Get the user's sequence from the database.
    sequence = get_sequence(user_id)

    # user_words = loads(sequence.body)
    # print "save_word_list(): User words:", user_words

    # Update the word list in the db.
    stored_words = loads(sequence.body)
    for word in word_list:
        # Append the words to any words already in the db.
        stored_words.append(word)

        # Update the full data entry part.
        # Since we're saving a whole list with no time information,
        # set the duration to be -1.
        if not sequence.data:
            sequence.data = '[{},{}]'.format(word, -1)
        else:
            sequence.data += '[{},{}]'.format(word, -1)

    sequence.body = dumps(stored_words)
    # print sequence.body
    sequence.timestamp = datetime.utcnow()

    # Update the database.
    db.session.add(sequence)
    db.session.commit()


def get_flow_time(user, sequence):
    start_time = get_start_time(user)
    if not start_time:
        return -1
    return (sequence.timestamp - start_time).total_seconds()


def get_total_time(user, answer):
    start_time = get_start_time(user)
    if not start_time:
        return -1
    return (answer.timestamp - start_time).total_seconds()


def get_tasks_time(sequence, answer):
    return (answer.timestamp - sequence.timestamp).total_seconds()


def get_start_time(user):
    name_list = user.username.split('_')
    if not name_list[-1].isdigit():
        return None
    time_str = name_list[-2] + '_' + name_list[-1]
    return datetime.strptime(time_str, "%Y-%m-%d_%H%M%S%f")
