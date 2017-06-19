"""
Subroutines for the thought dynamics flask application.
"""
from json import dumps, loads
from datetime import datetime
import os
from random import sample

from flask import request, session, Markup
from flask.ext.login import current_user
from boto.s3.connection import S3Connection

from application import db
from models import Sequence
from creativityconstruct import CreativityConstruct
from semilarconstruct import SemilarConstruct
from dataprocessor import dataprocessor, datareader
from utilslib import make_anon_id, get_flow_condition, CONDITION_FEEDBACK


LOAD_S3_CONSTRUCTS = False

# List of constructs on S3
S3_CONSTRUCT_NAMES = ['tasa_7']

if LOAD_S3_CONSTRUCTS:
    _construct_name = S3_CONSTRUCT_NAMES[0]
else:
    # Set default construct to be tasa_7
    _construct_name = 'tasa_7'
    # _construct_name = 'lyrics'

DEFAULT_EC2_DIRNAME = '/opt/python/etc/constructs/'
# DEFAULT_EC2_DIRNAME = '/home/ec2-user/constructs'
# DEFAULT_EC2_DIRNAME = 'c:/bin/constructs/tasa_7/'

"""Defaults for the deployment."""
CONSTRUCTS_PATH = 'constructs/'

_lemmatize = False

# Participants will first see one of these words.
SEED_WORDS = {'toaster', 'table', 'bear', 'snow', 'paper', 'candle'}

THOUGHT_CONSTRUCTS = {}
ABOUT_MESSAGES = {}
CONSTRUCTS_INFO = {}
FIRST_WORD = 'street'

WORD_MAX_COUNT = 20
MAX_COUNT_REACHED = -1

_creativity_threshold = .2

# S3 stuff
ACCESS_KEY_ID = 'ACCESS_KEY_ID'
ACCESS_KEY = 'ACCESS_KEY'

# Test globals.
_old_word = ''
_previous_word_list = []

all_user_words = {}

pairs_of_the_day = {}


def load_s3_constructs():
    c = S3Connection(ACCESS_KEY_ID, ACCESS_KEY)
    assert c
    b = c.get_bucket('s3_bucket')
    assert b

    constructs = {}
    for s3_c_name in S3_CONSTRUCT_NAMES:
        k_voc = b.get_key(s3_c_name + '_voc')
        k_lsa = b.get_key(s3_c_name + '_lsaModel')
        if not k_voc or not k_lsa:
            continue
        # For now all the constructs are TASA
        construct = SemilarConstruct(s3_c_name,
                                     '.',
                                     s3_key_voc=k_voc,
                                     s3_key_lsa=k_lsa)
        k_voc.close(fast=True)
        k_lsa.close(fast=True)
        constructs[s3_c_name] = construct
        CONSTRUCTS_INFO[s3_c_name] = [s3_c_name, CONSTRUCTS_PATH]

    c.close()

    return constructs


def load_ec2_constructs():
    ec2_dirname = DEFAULT_EC2_DIRNAME
    constructs = {}
    for s3_c_name in S3_CONSTRUCT_NAMES:
        """
        with open('/home/ec2-user/' + s3_c_name + '_voc', 'r') as f:
            k_voc = f.read()
        with open('/home/ec2-user/' + s3_c_name + '_lsaModel', 'r') as f:
            k_lsa = f.read()
        if not k_voc or not k_lsa:
            continue
        """
        dict_filename = ec2_dirname + s3_c_name + '_voc'
        lsi_filename = ec2_dirname + s3_c_name + '_lsaModel'
        # For now all the constructs are TASA
        construct = SemilarConstruct(s3_c_name,
                                     '',
                                     dict_filename=dict_filename,
                                     lsi_filename=lsi_filename)
        constructs[s3_c_name] = construct
        CONSTRUCTS_INFO[s3_c_name] = [s3_c_name, CONSTRUCTS_PATH]

    return constructs


def add_s3_constructs():
    s3_constructs = load_s3_constructs()
    THOUGHT_CONSTRUCTS.update(s3_constructs)
    for construct_name in S3_CONSTRUCT_NAMES:
        ABOUT_MESSAGES[construct_name] = load_about_message(construct_name)


def add_ec2_constructs():
    """XXX: finish implementing this."""
    ec2_constructs = load_ec2_constructs()

    THOUGHT_CONSTRUCTS.update(ec2_constructs)
    for construct_name in S3_CONSTRUCT_NAMES:
        ABOUT_MESSAGES[construct_name] = load_about_message(construct_name)


def load_about_message(construct_name):
    """
    Create construct information message.
    """
    construct_path = CONSTRUCTS_INFO[construct_name][1]
    about_message = "Construct name: "
    about_message += construct_name
    about_message += "\n"
    about_message += "Construct path: "
    about_message += construct_path
    about_message += "\n"

    """
    with open(construct_path + construct_name + '_corpora_log.txt') as \
            dict_file:
        about_message += "\n"
        about_message += "Construct LSA training log:\n"
        about_message += dict_file.read().decode('utf-8').encode('ascii',
                                                                 'replace')
     """

    return about_message


def check_files(pathname, extensions=('.dict', '.zip')):
    print 'These are the files in {}'.format(pathname)

    construct_num = 1
    construct_dict = {}
    for (dirpath, dirnames, filenames) in os.walk(pathname):
        for filename in filenames:
            # filename = eec_utils.get_filename(filename)
            # filename = os.path.splitext(filename)[0]
            fname, ext = os.path.splitext(filename)
            if ext.lower() in extensions:
                print '{} >>> {}'.format(construct_num, fname)
                if dirpath.endswith('/'):
                    constructpath = dirpath
                else:
                    constructpath = dirpath + '/'
                if filename.endswith('.zip'):
                    construct_dict[fname] = [fname, constructpath]
                else:
                    construct_dict[fname] = [fname, constructpath]
                construct_num += 1

    return construct_dict


def check_constructs(constructs_path):
    constructs = check_files(constructs_path)
    return constructs


def setup_constructs():
    global THOUGHT_CONSTRUCTS
    global ABOUT_MESSAGES
    global CONSTRUCTS_INFO
    global _old_word
    global _construct_name

    # Set working construct path.
    if os.path.isdir(DEFAULT_EC2_DIRNAME):
        print "Using ec2 constructs."
        working_path = DEFAULT_EC2_DIRNAME
    else:
        print "Using local constructs."
        working_path = CONSTRUCTS_PATH
        _construct_name = 'lyrics'

    CONSTRUCTS_INFO = check_constructs(working_path)
    for construct_name, construct_info in CONSTRUCTS_INFO.iteritems():
        construct_filename = construct_info[0]
        construct_path = construct_info[1]
        # XXX: Hack to differentiate between different types of constructs.
        if construct_name.lower().startswith('tasa'):
            new_construct = SemilarConstruct(construct_name,
                                             construct_path,
                                             load_zip=True)
        elif construct_name.lower().startswith('TASA'):
            new_construct = SemilarConstruct(construct_name,
                                             construct_path,
                                             load_zip=True)
        else:
            if construct_filename.endswith('.zip'):
                new_construct = None
                """XXX: gensim doesn't allow passing zip file streams.
                new_construct = CreativityConstruct(construct_name,
                                                    construct_path,
                                                    load_zip=True)
                """
            else:
                new_construct = CreativityConstruct(construct_name,
                                                    construct_path)
        THOUGHT_CONSTRUCTS[construct_name] = new_construct
        ABOUT_MESSAGES[construct_name] = load_about_message(construct_name)

    """XXX: Load S3 constructs now."""
    if LOAD_S3_CONSTRUCTS:
        # Now load constructs from S3
        add_s3_constructs()

    print 'Loaded {} constructs.'.format(len(THOUGHT_CONSTRUCTS))

    # XXX: Setup the _old_word global for now.
    _old_word = THOUGHT_CONSTRUCTS[_construct_name].get_random_word()

    # Set the default to tasa_7 if possible.
    if 'tasa_7' in THOUGHT_CONSTRUCTS:
        _construct_name = 'tasa_7'


# XXX: Setup up the constructs.
setup_constructs()
# Now load the global default about message.
_about_message = load_about_message(_construct_name)


def load_construct(construct_name=_construct_name):
    """Load a new construct for this session."""
    session['construct'] = construct_name

    # XXX: Now change the globals.
    global _old_word
    _old_word = THOUGHT_CONSTRUCTS[construct_name].get_random_word()


def display_constructs():
    for construct_num, construct_info in CONSTRUCTS_INFO.iteritems():
        print construct_info
    return CONSTRUCTS_INFO


def get_user_construct():
    try:
        construct_name = session['construct']
    except KeyError:
        # Custom construct not specified, go with the defaults.
        # print 'Construct not chosen, using default:', _construct_name
        construct_name = _construct_name
        session['construct'] = construct_name

    # print 'User construct:', session['construct']
    return THOUGHT_CONSTRUCTS[construct_name]


def get_user_count():
    try:
        count = session['count']
    except KeyError:
        count = 0
        session['count'] = count

    return count


def set_user_count(count):
    session['count'] = count


def get_creativity_threshold():
    return _creativity_threshold


def set_creativity_threshold(new_threshold):
    global _creativity_threshold
    _creativity_threshold = new_threshold
    return _creativity_threshold


def get_user_words():
    """Get a user's word list.

    XXX: Maybe in the future this should read from the database.
    """
    global all_user_words

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        # print 'user_id:', user_id
    else:
        try:
            user_id = session['anon_id']
        except KeyError:
            # print 'user_id not set'
            session['anon_id'] = make_anon_id()
            user_id = session['anon_id']

    if user_id not in all_user_words:
        all_user_words[user_id] = []

    return all_user_words[user_id]


def clear_user_words():
    global all_user_words

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        # print 'user_id:', user_id
    else:
        try:
            user_id = session['anon_id']
        except KeyError:
            # print 'user_id not set'
            session['anon_id'] = make_anon_id()
            user_id = session['anon_id']

    # print 'user id:', user_id
    """
    try:
        user_id = session['user_id']
    except KeyError:
        print 'user_id not set'
        user_id = 'Guest'
    """

    # Making sure the garbage is collected, to prevent mem leaks.
    if user_id not in all_user_words:
        all_user_words[user_id] = None
        all_user_words[user_id] = []
    else:
        all_user_words[user_id] = None
        all_user_words[user_id] = []


def get_sequence_id():
    try:
        sequence_id = session['sequence_id']
    except KeyError:
        sequence_id = None
    return sequence_id


def set_sequence_id(sequence_id):
    session['sequence_id'] = sequence_id
    # print session['sequence_id']


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


def run_thoughts():
    """Run the real-time forward flow analyses."""
    # print 'run_thoughts()'
    # XXX: Maybe we should clear the user's previous words.
    # clear_user_words()
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        user_id = make_anon_id()
    # print 'user_id:', user_id

    user_words = get_user_words()
    word_count = get_user_count()
    if word_count == 0:
        seed_word = get_seed_word()
        user_words.append(seed_word)
        output = Markup("<p>Seed word </p> <p>{}</p>".format(seed_word))
        setup_db_sequence(user_words, user_id)
    else:
        # print "Word count:", word_count
        # print "User words:", user_words
        try:
            seed_word = user_words[-1]
        except IndexError:
            # This happens when the server is reset. Which is unusual.
            # Reload from the database
            sequence_id = get_sequence_id()
            sequence = Sequence.query.filter_by(id=sequence_id).first()
            user_words = loads(sequence.body)
            seed_word = user_words[-1]
            print "Word cache for user id {} re-synced from db".format(user_id)
        output = Markup("<p>Previous word </p> <p>{}</p>".format(seed_word))

    return output, seed_word, user_words, word_count


def get_sequence(user_id):
    """
    Get this user's sequence from the database.
    If no sequence exists, create one.
    """
    sequence = Sequence.query.filter_by(user_id=user_id).\
        order_by(Sequence.id.desc()).first()
    if not sequence:
        user_sequence = [get_seed_word()]
        sequence = setup_db_sequence(user_sequence, user_id)
        # print "Created new sequence for", user_id, ":", user_sequence
    return sequence


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


def flow_step():
    """
    Record the next step of the flow
    Called by:
    @application.route('/process_thoughts', methods=['GET', 'POST'])
    process_thoughts()
    """
    # print 'flow_step()'
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        user_id = make_anon_id()

    # Get the user's sequence from the database.
    user_sequence = get_sequence(user_id)
    user_words = loads(user_sequence.body)
    # print "flow_step(): User words:", user_words

    # Include the seed word in the count.
    word_count = len(user_words)
    # print "Word count:", word_count

    text = "No return"
    return_val = 0
    similarity = None
    sim_text = ''
    if request.method == 'POST':
        # print("Next flow step args:", request.args)
        # print("Next flow step form:", request.form)
        word = request.form['thought']
        if word != '':
            if 'duration' in request.form:
                duration = request.form['duration']
            else:
                duration = -1
            # print "user words"
            # print user_words
            last_word = user_words[-1]
            # print "last word"
            # print last_word
            similarity = query_pair(word, last_word)
            # print "similarity"
            # print similarity
            # print _creativity_threshold
            condition = get_flow_condition(user_id)
            if not similarity:
                sim_text = "Please try a different word."
            elif condition == CONDITION_FEEDBACK:
                if similarity > _creativity_threshold:
                    sim_text = "Too similar to previous words. "
                    sim_text += "Please try a different word."
                else:
                    # Save this word.
                    user_words.append(word)
                    # Update the database.
                    save_word_data_to_db(word, duration, user_sequence)
                    # Keep track of user's word count.
                    word_count += 1
                    # set_user_count(word_count)
            else:
                # Save this word.
                user_words.append(word)
                # Update the database.
                save_word_data_to_db(word, duration, user_sequence)
                # Keep track of user's word count.
                word_count += 1
                # set_user_count(word_count)
            # print sim_text

            # Set message text about previous word.
            text = word

            # Check the word count.
            if word_count >= WORD_MAX_COUNT:
                # print 'Max words reached:', word_count
                return_val = MAX_COUNT_REACHED
            else:
                return_val = word_count

        else:
            # Didn't get a word.
            text = 'Please enter a word.'
    else:
        # This function shouldn't be called from a GET request.
        if request.method == 'GET':
            print "flow_step() got a GET request!!", request.args
            text = "Please enter a word."
    output = dumps({'text': text,
                    'wordlist': list(reversed(user_words)),
                    'wordcount': len(user_words),
                    'similarity': similarity,
                    'simtext': sim_text,
                    'return_val': str(return_val)})
    # print output
    return output


def save_word_data_to_db(word, duration, sequence):
    # Update the database.
    stored_words = loads(sequence.body)
    stored_words.append(word)
    sequence.body = dumps(stored_words)
    if not sequence.data:
        sequence.data = '[{},{}]'.format(word, duration)
    else:
        sequence.data += '[{},{}]'.format(word, duration)
    db.session.add(sequence)
    db.session.commit()


def save_single_word_with_sequence(word, duration=-1, sequence=None):
    """Save a single word to the db."""
    if not sequence:
        if current_user.is_authenticated:
            user_id = current_user.get_id()
        else:
            user_id = make_anon_id()

        # Get the user's sequence from the db.
        sequence = get_sequence(user_id)

    # Get the previous words already in the db.
    stored_words = loads(sequence.body)

    # Append the word to any words already in the db.
    stored_words.append(word)

    # Update the full data entry part.
    # If we're saving a word with no time information,
    # set the duration to be -1.
    if not sequence.data:
        sequence.data = '[{},{}]'.format(word, duration)
    else:
        sequence.data += '[{},{}]'.format(word, duration)

    sequence.body = dumps(stored_words)
    # print sequence.body
    sequence.timestamp = datetime.utcnow()

    # Update the database.
    db.session.add(sequence)
    db.session.commit()


def save_single_word(word):
    """Save a single word to the db."""
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        user_id = make_anon_id()

    # Get the user's sequence from the database.
    # sequence = get_sequence(user_id)
    sequence = Sequence.query.filter_by(user_id=user_id).\
        order_by(Sequence.id.desc()).first()

    if sequence:
        # Update the word list in the db.
        stored_words = loads(sequence.body)
        # Append the word to any words already in the db.
        stored_words.append(word)
        sequence.body = dumps(stored_words)
    else:
        # Update the word list.
        stored_words = [word]
        # Save the words and get the new sequence.
        sequence = setup_db_sequence(stored_words, user_id)

    # Update the full data entry part.
    # Since we're saving a whole list with no time information,
    # set the duration to be -1.
    if not sequence.data:
        sequence.data = '[{},{}]'.format(word, -1)
    else:
        sequence.data += '[{},{}]'.format(word, -1)

    sequence.timestamp = datetime.utcnow()

    # Update the database.
    db.session.add(sequence)
    db.session.commit()




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


def store_word_data(word, duration):
    # Update the database.
    sequence_id = get_sequence_id()
    if sequence_id:
        sequence = Sequence.query.filter_by(id=sequence_id).first()
        stored_words = loads(sequence.body)
        stored_words.append(word)
        sequence.body = dumps(stored_words)
        if not sequence.data:
            sequence.data = '[{},{}]'.format(word, duration)
        else:
            sequence.data += '[{},{}]'.format(word, duration)
        # print sequence.body
        db.session.add(sequence)
        db.session.commit()
    else:
        print "No sequence id set!"


def word_recorder():
    """Record word inputs.
    Called by:
    @application.route('/process_thoughts', methods=['GET', 'POST'])
    process_thoughts()
    """
    user_words = get_user_words()
    word_count = get_user_count()

    text = "No return"
    return_val = 0
    similarity = None
    if request.method == 'POST':
        # print("let's process some thoughts", request.args)
        word = request.form['thought']
        if word != '':
            duration = request.form['duration']
            user_words.append(word)
            text = word

            # Keep track of user's word count.
            word_count += 1
            set_user_count(word_count)

            # Check the word count.
            if word_count >= WORD_MAX_COUNT:
                # print 'Max words reached:', word_count
                return_val = MAX_COUNT_REACHED
            else:
                return_val = word_count

            # Update the database.
            store_word_data(word, duration)
        else:
            # Didn't get a word.
            text = 'Please enter a word.'
    else:
        # This function shouldn't be called from a GET request.
        if request.method == 'GET':
            print "word_recorder() got a GET request!!", request.args
            text = "Please enter a word."
    output = dumps({'text': text,
                    'wordlist': list(reversed(user_words)),
                    'wordcount': len(user_words),
                    'similarity': similarity,
                    'return_val': str(return_val)})
    return output


def query_pair(word1, word2):
    thought_construct = get_user_construct()
    # Get the cosine similarity between the LSI vectors of these two words.
    similarity = thought_construct.query_pair_lsi(word1, word2)
    """
    if similarity:
        print "  Word pair:", word1, "and", word2
        print "  Cosine similarity is", round(similarity, 3)
    else:
        print "  Probably \"{}\" isn't in the dictionary.".format(word2)
    """

    return similarity


def query_pair_distance(word1, word2):
    thought_construct = get_user_construct()
    # Get the cosine distance between the LSI vectors of these two words.
    distance = thought_construct.query_pair_lsi_distance(word1, word2)
    return distance


def list_query(word_list):
    thought_construct = get_user_construct()
    result = thought_construct.query_list(word_list)
    return result


def list_query_distance(word_list):
    thought_construct = get_user_construct()
    result = thought_construct.query_list_distance(word_list)
    return result


def matrix_to_str(matrix):
    output_str = ""
    for row in matrix:
        output_str += ",".join(map(str, row))
        output_str += ";"
    return output_str


def thought_processor():
    """Process word inputs.
    Called by:
    @application.route('/process_thoughts', methods=['GET', 'POST'])
    process_thoughts()
    """
    global _old_word

    user_words = get_user_words()
    word_count = get_user_count()

    text = "No return"
    return_val = 0
    similarity = None
    if request.method == 'POST':
        # print("let's process some thoughts", request.args)
        thought = request.form['thought']
        if thought != '':
            # print "new word:", thought
            duration = request.form['duration']
            # print 'duration:', duration
            # print 'type', type(duration)

            """ Could check in the future if this word has been said before.
            if thought in set(user_words):
                pass
            """
            output = query_pair(_old_word, thought)
            if output:
                similarity = round(output, 3)
                text = 'Similarity between {} and {} is \
                              {}'.format(_old_word,
                                         thought,
                                         similarity)
            else:
                similarity = None
                text = "Choose a different word besides \
                              \"{}\"".format(thought)

            _old_word = thought
            user_words.append(thought)

            # Keep track of user's word count.
            word_count += 1
            set_user_count(word_count)

            # Check the word count.
            if word_count >= WORD_MAX_COUNT:
                # print 'Max words reached:', word_count
                return_val = MAX_COUNT_REACHED
            else:
                return_val = word_count

            # Update the database.
            sequence_id = get_sequence_id()
            if sequence_id:
                sequence = Sequence.query.filter_by(id=sequence_id).first()
                # XXX: The simplest way. Maybe not the safest, since it might
                # overwrite old words?
                # I think there will be old words
                # only during development though.
                sequence.body = dumps(user_words)
                if not sequence.data:
                    sequence.data = '[{},{}]'.format(thought, duration)
                else:
                    sequence.data += '[{},{}]'.format(thought, duration)
                # print sequence.body
                db.session.add(sequence)
                db.session.commit()
        else:
            # Didn't get a word.
            text = 'Please enter a word.'
    else:
        # This function shouldn't be called from a GET request.
        if request.method == 'GET':
            # print("Got a GET request!!", request.args)
            text = "Please enter a word."
    output = dumps({'text': text,
                    'wordlist': list(reversed(user_words)),
                    'wordcount': len(user_words),
                    'similarity': similarity,
                    'return_val': str(return_val)})
    return output


# @application.route('/reset_thoughts', methods=['GET', 'POST'])
def thought_reseter():
    clear_user_words()
    set_user_count(0)

    seed_word = get_seed_word()

    """ XXX: Don't record this.
    user_words = get_user_words()
    user_words.append(seed_word)

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        # print 'user_id:', user_id
        setup_db_sequence(user_words, user_id)
    """

    """XXX: This doesn't work because of the client-side js.
    output = Markup("<p>Seed word </p> <p>{}</p>".format(seed_word))
    """

    text = "The restart word is {}.".format(seed_word)

    # return_val = {'text': text, 'wordlist': [_old_word]}
    output = dumps({'text': text,
                    'wordlist': [seed_word],
                    'wordcount': 0,
                    'return_val': str(0)})
    # print "output", dumps(return_val)
    return output


def get_relatedness_average(avg_word):
    thought_construct = get_user_construct()
    return thought_construct.get_sampled_avg(avg_word)


def get_closest_words(close_word):
    thought_construct = get_user_construct()
    # Check how many iterations we should do.
    # -1 be in string form, and won't show up as isdigit()
    if request.form['close_iterations'] == '-1':
        iterations = None
    elif request.form['close_iterations'] != '' and \
            request.form['close_iterations'].isdigit():
        iterations = int(request.form['close_iterations'])
    else:
        # All other cases, go with 2500.
        iterations = 2500

    # Check how many closest words to get.
    if request.form['num_closest'] != '' and \
            request.form['num_closest'].isdigit():
        num_closest = int(request.form['num_closest'])
        return thought_construct.get_closest(close_word,
                                             num=num_closest,
                                             iterations=iterations)
    else:
        return thought_construct.get_closest(close_word,
                                             iterations=iterations)


def compare_random():
    thought_construct = get_user_construct()
    if request.form['random_word'] == '':
        word = None
    else:
        word = request.form['random_word']
    return thought_construct.compare_random(word)


def compare_pair():
    thought_construct = get_user_construct()
    word1 = request.form['pair_word1']
    word2 = request.form['pair_word2']
    if word1 == '' and word2 == '':
        return thought_construct.compare_random()
    elif word1 == '':
        return thought_construct.compare_random(word2)
    elif word2 == '':
        return thought_construct.compare_random(word1)
    else:
        similarity = thought_construct.query_pair_lsi(word1, word2)
    return similarity, word1, word2


def get_potd(day):
    try:
        return pairs_of_the_day[day]
    except KeyError:
        pairs_of_the_day[day] = get_2_pairs()
        return pairs_of_the_day[day]


def get_2_pairs():
    thought_construct = THOUGHT_CONSTRUCTS[_construct_name]

    # Get a first pair with > .3 similarity, or best out of 30.
    sim1, word1a, word1b = compare_random_pair(thought_construct)
    for i in range(0, 30):
        if sim1 > 0.3:
            break
        sim3, word3a, word3b = compare_random_pair(thought_construct)
        if sim3 > sim1:
            sim1, word1a, word1b = sim3, word3a, word3b

    # Get closest matched similarity out of 30 tries.
    sim2, word2a, word2b = compare_random_pair(thought_construct)
    lowest_diff = abs(sim1 - sim2)
    for i in range(0, 30):
        sim3, word3a, word3b = compare_random_pair(thought_construct)
        this_diff = abs(sim1 - sim3)
        if this_diff < lowest_diff:
            sim2, word2a, word2b = sim3, word3a, word3b
            lowest_diff = this_diff
    # print "Pair matching difference is", lowest_diff

    return thought_construct.name, \
        (sim1, word1a, word1b), \
        (sim2, word2a, word2b)


def compare_random_pair(thought_construct=None):
    if not thought_construct:
        thought_construct = get_user_construct()
    word1 = thought_construct.get_random_word()
    word2 = thought_construct.get_random_word()
    similarity = thought_construct.query_pair_lsi(word1, word2)
    return similarity, word1, word2


def get_random_word():
    thought_construct = get_user_construct()
    return thought_construct.get_random_word()


# @application.route('/save_words', methods=['GET', 'POST'])
def word_saver():
    print "Save the words."
    if request.method == 'POST':
        if current_user.is_authenticated:
            user_id = current_user.get_id()
            # print 'user_id:', user_id
        else:
            text = "User isn't logged in!"
            return_val = {'text': text, 'wordlist': [_old_word]}
            # print 'save_words():', dumps(return_val)
            return dumps(return_val)

        user_words = get_user_words()

        sequence_id = get_sequence_id()

        text = dumps(user_words)
        # print text
        # print type(text)

        if sequence_id:
            sequence = Sequence.query.filter_by(id=sequence_id).first()
            # XXX: The simplest way. Maybe not the safest, since it might
            # overwrite old words?
            # I think there will be old words
            # only during development though.
            sequence.body = dumps(user_words)
            if not sequence.data:
                sequence.data = ''
            # print sequence.body
        else:
            sequence = Sequence(body=dumps(user_words),
                                data='',
                                user_id=user_id,
                                user=current_user._get_current_object(),
                                timestamp=datetime.utcnow())

        db.session.add(sequence)
        db.session.commit()

        # print 'Posted words'
        pass
    else:
        # print 'Weird'
        text = "Invalid method"

    return_val = {'text': text, 'wordlist': [_old_word]}

    # print 'save_words():', dumps(return_val)
    return dumps(return_val)


def process_word_lists(word_lists, user_list=None, get_distance=False):
    all_word_list = []
    all_user_data = {}
    thought_construct = get_user_construct()
    # If we don't have a user list, make a numeric list of users.
    if not user_list:
        user_list = range(0, len(word_lists))

    for this_word_list, p_id in zip(word_lists, user_list):
        user_data = {}
        user_data['words'] = this_word_list
        user_data['p_id'] = p_id
        all_word_list.append(this_word_list)

        if get_distance:
            result = thought_construct.query_list_distance(this_word_list)
        else:
            result = thought_construct.query_list(this_word_list)

        text = format_pw(this_word_list, result)
        if not text:
            text = "Something weird happened with \
                          \"{}\"".format(p_id)
        user_data['results'] = result
        user_data['results_text'] = text
        all_user_data[p_id] = user_data
    return all_user_data


def process_word_lists_file_str(words_file, get_distance=False):
    words_file_list = words_file.splitlines()
    thought_construct = get_user_construct()
    # header = words_file_list[0]
    all_word_list = []
    all_user_data = {}
    for line in words_file_list[1:]:
        user_data = {}
        line = line.strip()
        line_list = line.split(',')

        p_id = line_list[0]
        user_data['p_id'] = p_id

        word_list = line_list[1:]
        # print "word list:", word_list
        user_data['words'] = word_list
        all_word_list.append(word_list)

        if get_distance:
            result = thought_construct.query_list_distance(word_list)
        else:
            result = thought_construct.query_list(word_list)

        text = format_pw(word_list, result)
        if text:
            # Not using this right now.
            # return_val = 0
            pass
        else:
            text = "Something weird happened with \
                          \"{}\"".format(line)
        user_data['results'] = result
        user_data['results_text'] = text
        all_user_data[p_id] = user_data
    return all_user_data


def construct_do_list(in_word_list=None):
    """
    Run query_list.
    Reached by @application.route('/query_list', methods=['GET', 'POST'])
    """
    thought_construct = get_user_construct()
    text = "No return"
    word_list = []
    # Not using this right now.
    # return_val = 1
    if request.method == 'POST':
        if in_word_list:
            # print 'in_word_list:', in_word_list
            thought = in_word_list
        else:
            thought = request.form['thought']
        if thought != '':
            temp_list = thought.split()
            for word in temp_list:
                # Get rid of leading or trailing ','
                word = word.strip(',')
                word_list += word.split(',')
            # print "word list:", word_list
            query_result = thought_construct.query_list(word_list)
            text = format_pw(word_list, query_result)
            if text:
                # Not using this right now.
                # return_val = 0
                pass
            else:
                text = "Something weird happened with \
                              \"{}\"".format(thought)
        else:
            text = 'Please say something.'
    else:
        if request.method == 'GET':
            # print("Got a GET request!!", request.args)
            text = "Unknown request"
    """Don't remember what this is for.
    output = dumps({'text': text,
                         'wordlist': ['empty', 'list'],
                         'similarity': 0,
                         'return_val': str(return_val)})
    """
    """
    return render_template(
        'research.html',
        title='Research',
        message='Do research stuff.',
        output=text)
    """
    return word_list, text


def analyze_word_list(word_list):
    thought_construct = get_user_construct()
    return thought_construct.query_list_distance(word_list)


def calc_output_avg(matrix):
    """Calculate average from results matrix. The matrix for hi, bye
    looks like this:
    [[u'hi', '1.0', '-0.458'], [u'bye', '-0.458', '1.0']]
    """
    total = 0.0
    count = 0
    for i in range(0, len(matrix)):
        row = matrix[i]
        for j in range(i+1, len(row)):
            # Skip the entry for the comparison
            # for the word with itself.
            try:
                total += row[j]
            except TypeError:
                continue
            except:
                raise
            count += 1

    try:
        total_avg = total / count
    except ZeroDivisionError:
        total_avg = None
    except:
        raise
    return total_avg


def format_pw(word_list, result):
    """ Create formatted output to send to user. """
    # Start with a ' ' for the top row.
    output = []
    word_index = 0
    out_index = 0
    for row in result:
        output.append([word_list[word_index]])
        for similarity in row:
            try:
                output[out_index].append(str(round(similarity, 3)))
            except TypeError:
                output[out_index].append('')
            except:
                raise
        word_index += 1
        out_index += 1

    return output


def format_pw_out(word_list, result):
    """ Create formatted output to send to user. """
    # Start with a ' ' for the top row.
    output = [['']]
    for word in word_list:
        output[0].append(word)
    word_index = 0
    out_index = 1
    for row in result:
        output.append([word_list[word_index]])
        for similarity in row:
            if similarity:
                output[out_index].append(str(round(similarity, 3)))
            else:
                output[out_index].append('')
        word_index += 1
        out_index += 1

    return output


def format_csv_str_list(csv_str_list):
    csv_list = []
    for data_line in csv_str_list:
        csv_list.append(data_line.strip().split(','))
    return csv_list


def analyze_file_stream(p_data_stream, prefix='file_'):
    thought_construct = get_user_construct()
    # output_data = dataprocessor.model_battle(thought_construct)
    output_data = \
        dataprocessor.analyze_stream(thought_construct, p_data_stream, prefix)
    # print 'output_data', output_data
    return format_csv_str_list(output_data)


def run_model_battle(p_data_file='drama.csv', prefix='drama_'):
    thought_construct = get_user_construct()
    # output_data = dataprocessor.model_battle(thought_construct)
    output_data = \
        dataprocessor.model_battle(thought_construct,
                                   p_data_file=p_data_file,
                                   prefix=prefix)
    # print output_data
    return format_csv_str_list(output_data)


def get_words(filename='drama.csv',
              file_stream=None,
              return_csv=False,
              save_data=False,
              savename=None):
    if file_stream:
        all_p_data = datareader.read_stream(filename)
    else:
        all_p_data = datareader.read_data(filename)
    header = "p_id"
    for i in range(1, 21):
        heading = ',word_' + str(i)
        header += heading
    header += "\n"
    # print header
    words_output = [header]
    sorted_p_ids = sorted(all_p_data)
    # for p_id, p_data in all_p_data.iteritems():
    for p_id in sorted_p_ids:
        p_data = all_p_data[p_id]
        line_output = p_id
        if p_data['words']:
            for word in p_data['words']:
                line_output += ','
                line_output += word
        line_output += "\n"
        words_output.append(line_output)
    # print words_output
    if return_csv:
        return format_csv_str_list(words_output)
    else:
        return words_output


def filename_maker(prefix='output_', ext='.csv'):
    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = prefix + curr_time + ext
    return filename


def write_out_list(output_data, filename=None):
    if not filename:
        filename = filename_maker()
    with open(filename, 'w') as f:
        for line in output_data:
            f.write(line)


def get_seed_word(user_id=None):
    if user_id:
        user_sequence = get_sequence(user_id)
        user_words = loads(user_sequence.body)
        seed_word = user_words[0]
    else:
        seed_word = sample(SEED_WORDS, 1)[0]
    return seed_word


def get_set_seed_word():
    seed_word = sample(SEED_WORDS, 1)[0]
    save_single_word(seed_word)
    return seed_word
