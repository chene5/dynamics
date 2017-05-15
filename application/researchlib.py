"""
Research functions.
"""
from datetime import datetime

from flask import render_template, request, make_response
from flask.ext.login import current_user

import thoughtslib
from dataprocessor import dataprocessor


def do_research():
    """
    Renders the research page, which has extra functionality
    for doing research.
    """
    message = "Researchers' secret page"
    if 'getWords' in request.form:
        words_output = thoughtslib.get_words()
        message = "Here are words"
        if 'saveData' in request.form:
            thoughtslib.write_out_list(words_output)
        output = thoughtslib.format_csv_str_list(words_output)
        return message, output
    elif 'getCreatThresh' in request.form:
        message = 'Creativity threshold is:', \
            thoughtslib.get_creativity_threshold()
    elif 'setCreatThresh' in request.form:
        try:
            new_threshold = float(request.form['newCreatThresh'])
            new_threshold = thoughtslib.set_creativity_threshold(new_threshold)
        except ValueError:
            new_threshold = thoughtslib.get_creativity_threshold()
        except:
            raise
        message = 'New creativity threshold is:', new_threshold
    elif 'battleDrama' in request.form:
        message = 'Results of the drama battle'
        output = thoughtslib.run_model_battle(p_data_file='drama_short.csv',
                                              prefix='drama_')
        return message, output
    elif 'battleField' in request.form:
        message = 'Results of the field battle'
        output = thoughtslib.run_model_battle(p_data_file='field_short.csv',
                                              prefix='field_')
        return message, output
    elif 'battleFile' in request.form:
        message = 'Results of the battle'
        stream = get_file_contents()
        if not stream:
            return render_template(
                'research.html',
                year=datetime.now().year,
                username=get_username(),
                title="File upload failed",
                message='No file analyzed',
            )
        output = thoughtslib.analyze_file_stream(stream,
                                                 prefix='drama_')
        response = gen_csv(word_list=None, input_list=output)
        return response
    elif 'battleDramaSave' in request.form:
        message = 'Results of the drama battle'
        output = thoughtslib.run_model_battle(p_data_file='drama_short.csv',
                                              prefix='drama_')
        response = gen_csv(word_list=None, input_list=output)
        return response
    elif 'battleFieldSave' in request.form:
        message = 'Results of the field battle'
        output = thoughtslib.run_model_battle(p_data_file='field_short.csv',
                                              prefix='field_')
        response = gen_csv(word_list=None, input_list=output)
        return response
    elif 'analyzeDrama' in request.form:
        message = 'Matrices of Drama words'
        output = process_word_list('drama_short_words.csv')
        return message, output
    elif 'analyzeField' in request.form:
        message = 'Matrices of Drama words'
        output = process_word_list('field_short_words.csv')
        return message, output
    elif 'analyzeWordsFile' in request.form:
        response = process_word_list_file()
        if response:
            return response
        else:
            message = 'No file uploaded'
    elif 'upload' in request.form:
        response = analyze_file()
        if response:
            return response
        else:
            message = 'No file uploaded'
    elif 'wordsFromFile' in request.form:
        response = analyze_file(file_stream=True)
        if response:
            return response
        else:
            message = 'No file uploaded'
    return render_template(
        'research.html',
        year=datetime.now().year,
        username=get_username(),
        title='Researcher page',
        message=message)


def analyze_file(file_stream=False, return_csv=True):
    # print 'analyze_file()'
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies
    print 'request.files:', request.files
    """
    file_contents = get_file_contents()
    if not file_contents:
        return None
    # print 'file_contents:', file_contents[:6]
    # print 'type of file_contents:', type(file_contents)

    output = thoughtslib.get_words(file_contents,
                                   file_stream=file_stream,
                                   return_csv=return_csv)
    # output = thoughtslib.analyze_file_stream(file_contents, file_stream)
    # print 'output:', output
    response = gen_csv(word_list=None, input_list=output)

    return response


def process_word_list(words_file):
    """Process csv of word lists."""
    with open(words_file, 'r') as f:
        all_user_data = thoughtslib.process_word_lists(f.read())

    all_computed_data = {}
    for user, data in all_user_data.iteritems():
        corr_data, overall_data = dataprocessor.compute_all(data['results'],
                                                            data['words'])
        # print 'user:', user
        # print corr_data
        # print overall_data
        all_computed_data[user] = \
            {'corr_data': corr_data, 'overall_data': overall_data}
    output = gen_all_user_data_list(all_user_data, all_computed_data)
    return output


def gen_all_user_data_list(all_user_data, all_computed_data):
    # XXX: Need to fix this hard-coded header!!!
    header = 'SN,,,,,,,,,,,,,,,,,,,,,,,ALL,FUTURE,PAST,N-1,N-2,N-3,NAs'
    data_list = [header.split(',')]

    try:
        sorted_p_ids = sorted(all_user_data, key=int)
    except ValueError:
        sorted_p_ids = sorted(all_user_data)
    for p_id in sorted_p_ids:
        user_data = all_user_data[p_id]
        computed_data = all_computed_data[p_id]
        corr_data = computed_data['corr_data']
        overall_data = computed_data['overall_data']

        # print user_data

        subheader = p_id
        subheader += ',Document'
        for word in user_data['words']:
            subheader += ',' + word
        # subheader += '\n'
        data_list.append(subheader.split(','))

        first_line = True
        for word, results_line in zip(user_data['words'],
                                      user_data['results']):
            line = ',' + word
            for result in results_line:
                line += ','
                if result:
                    line += str(round(result, 3))
                else:
                    line += '.'
            line += ','
            try:
                line += str(round(corr_data[word]['all'], 3))
            except TypeError:
                line += '.'
            line += ','
            try:
                line += str(round(corr_data[word]['future'], 3))
            except TypeError:
                line += '.'
            line += ','
            try:
                line += str(round(corr_data[word]['past'], 3))
            except TypeError:
                line += '.'
            # line += '\n'
            if first_line:
                line += ','
                line += str(overall_data['n_1'])
                line += ','
                line += str(overall_data['n_2'])
                line += ','
                line += str(overall_data['n_3'])
                line += ','
                line += str(overall_data['n_a'])
                first_line = False
            data_list.append(line.split(','))
        # XXX: Need to fix this hard-coded header!!!
        gap_line = ',,,,,,,,,,,,,,,,,,,,,,,{},{},{},{},,,'.format(
            overall_data['all'],
            overall_data['future'],
            overall_data['past'],
            overall_data['weighted'])
        data_list.append(gap_line.split(','))

    return data_list


def process_word_list_file():
    """Process csv of word lists."""
    file_contents = get_file_contents()
    if not file_contents:
        return None

    all_user_data = thoughtslib.process_word_lists(file_contents)
    all_computed_data = {}
    for user, data in all_user_data.iteritems():
        corr_data, overall_data = dataprocessor.compute_all(data['results'],
                                                            data['words'])
        # print 'user:', user
        # print corr_data
        # print overall_data
        all_computed_data[user] = \
            {'corr_data': corr_data, 'overall_data': overall_data}

    # response = gen_data_file(all_user_data)
    output = gen_all_user_data_list(all_user_data, all_computed_data)
    response = gen_csv(word_list=None, input_list=output, prefix='matrices_')

    return response


def gen_data_file(all_user_data):
    file_str = gen_file_str(all_user_data)

    response = make_response(file_str)
    filename = gen_filename()

    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'

    return response


def gen_file_str(all_user_data):
    header = 'SN,,,,,,,,,,,,,,,,,,,,,,ALL,FUTURE,PAST,N-1,N-2,N-3,NAs\n'
    file_str = header

    try:
        sorted_p_ids = sorted(all_user_data, key=int)
    except ValueError:
        sorted_p_ids = sorted(all_user_data)
    for p_id in sorted_p_ids:
        user_data = all_user_data[p_id]

        subheader = p_id
        for word in user_data['words']:
            subheader += ',' + word
        subheader += '\n'
        file_str += subheader

        for results_line in user_data['results']:
            line = ''
            for result in results_line:
                line += ','
                if result:
                    line += str(round(result, 3))
                else:
                    line += '.'
            line += '\n'
            file_str += line
        gap_line = ',,,,,,,,,,,,,,,,,,,,,,0.666,0.666,0.666,,,,\n'
        file_str += gap_line

    return file_str


def gen_filename():
    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return 'results_' + curr_time + '.csv'


def gen_csv(word_list=None, input_list=None, prefix='results_'):
    csv_str = make_csv_str(word_list, input_list)
    # print 'csv_str:', csv_str

    response = make_response(csv_str)

    curr_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = prefix + curr_time + '.csv'
    # print 'filename:', filename

    response.headers["Content-Disposition"] = "attachment; filename=" + \
        filename
    response.mimetype = 'text/csv'

    return response


def get_file_contents():
    # print 'get_file_contents()'
    """
    print 'request.form:', request.form
    print 'request.args:', request.args
    print 'request.values:', request.values
    print 'request.data:', request.data
    print 'request.cookies:', request.cookies
    print 'request.files:', request.files
    """
    if not request.files:
        return None

    for infilename, infile in request.files.iteritems():
        if not infile:
            return None

    # print 'infile:', infile
    # print 'type for infile', type(infile)
    # output = thoughtslib.analyze_file_stream(infile.stream)

    stream = infile.stream.read()
    """
    try:
        stream = infile.stream.read().decode("utf-8")
    except UnicodeDecodeError:
        try:
            print 'File not encoded in utf-8. Trying latin-1'
            stream = infile.stream.read().decode("latin-1")
        except:
            print 'Not in utf-8 or latin-1'
            raise
    """
    return stream


def get_username():
    return current_user.username


def make_csv_str(word_list=None, input_list=None):
    # print 'input_list:', input_list
    if word_list:
        csv_str = ','
        for word in word_list[-1]:
            csv_str += word + ','
        csv_str += word_list[-1]
        csv_str += '\n'
    else:
        csv_str = ''

    for row in input_list:
        for item in row[:-1]:
            if item == '\n':
                continue
            csv_str += str(item) + ','
        csv_str += row[-1]
        csv_str += '\n'
    return csv_str
