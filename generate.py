'''Generate song lyrics with an N-gram model based on data extracted from
existing lyrics.
'''
import argparse
import os
import random
import sys
from collections import deque

import process
from process import NGRAMS, LINES_PER_VERSE, TOKENS_PER_LINE
from process import START_LINE_TOKEN, END_LINE_TOKEN

COMMON_POP_SONG_STRUCTURE = ['Verse 1', 'Chorus', 'Verse 2', 'Chorus',
        'Bridge', 'Chorus']
N_GRAM_SIZE_INVALID_MESSAGE = 'N-gram size must be a positive integer'

def choose_next_token(state_chain, ngram_frequency):
    '''Choose a random next token and update the state_chain.

    Randomly sample a next token from the frequency distribution given by
    traversing the ngram_frequency dictionary by the tokens in state_chain, and
    update the state_chain (i.e. append the new token, pushing the leftmost
    token off).
    Arguments:
    state_chain - a deque containing the n-1 previous tokens chosen, with
            maximum length n-1
    ngram_frequency - a nested dictionary representing the frequency of n-grams
            (i.e. has depth 1 greater than the length of state_chain)
    '''
    next_token_dist = ngram_frequency
    for token in state_chain:
        next_token_dist = next_token_dist[token]

    next_token = sample_from_frequencies(next_token_dist)
    state_chain.append(next_token)
    return next_token

def collect_files(path_list, recursive):
    '''Collect the list of filenames specified by the given paths.

    Given a list of paths from the command line, returns a list of the all the
    filenames either directly specified as a path or contained in a directory
    specified as a path. If recursive is True, recursively searches into
    directories; else only includes the files immediately within each directory
    path.
    '''
    files_list = []
    for path in path_list:
        if os.path.isfile(path):
            files_list.append(path)

        elif os.path.isdir(path):
            if recursive:
                for root, dirs, files, in os.walk(path):
                    files_list += [os.path.join(root, f) for f in files]
            else:
                pathnames = [os.path.join(path, name) for name in
                        os.listdir(path)]
                files_list += filter(os.path.isfile, pathnames)

        # TODO: add else case that raises an exception for invalid path

    return files_list

def create_line(ngram_frequencies, n):
    '''Creates a line of a song.

    Arguments:
    ngram_frequencies - the n-gram frequencies from the collected lyrics data
    n - the n-gram size to use; cannot be greater than the largest n-gram size
            in ngram_frequencies
    '''
    # Store the previous n-1 tokens in a deque
    state_chain = deque([START_LINE_TOKEN for i in xrange(n-1)], n-1)
    tokens = []
    token = choose_next_token(state_chain, ngram_frequencies[n])

    while token != END_LINE_TOKEN: # Let probability determine line length
        tokens.append(token)
        token = choose_next_token(state_chain, ngram_frequencies[n])

    return smart_capitalize(' '.join(tokens))

def create_section(ngram_frequencies, num_lines, n):
    '''Creates a section of a song num_lines long.

    Arguments:
    ngram_frequencies - the n-gram frequencies from the collected lyrics data
    num_lines - number of lines to put in the section
    n - the n-gram size to use; cannot be greater than the largest n-gram size
            in ngram_frequencies
    '''
    lines = []
    for i in xrange(num_lines):
        lines.append(create_line(ngram_frequencies, n))

    return '\n'.join(lines)

def create_song(frequency_data, structure, n):
    '''Create a song with a specified structure from the frequency_data.

    Arguments:
    frequency_data - a data dictionary of the form returned by
            process.py:collect_data
    structure - a list of strings representing the sections of the song;
            identical strings represent repeated sections (e.g. choruses)
    n - the n-gram size to use; cannot be greater than the largest n-gram size
            that data was collected for in frequency_data
    '''
    lpv_frequencies = frequency_data[LINES_PER_VERSE]
    song_parts = {}

    for section in structure:
        if section not in song_parts:
            song_parts[section] = create_section(frequency_data[NGRAMS],
                    sample_from_frequencies(lpv_frequencies), n)

    return '\n\n'.join(['[%s]\n%s' % (section, song_parts[section]) for section
            in structure])

def get_cl_args():
    '''Get the command line arguments using argparse.'''
    arg_parser = argparse.ArgumentParser(
            description='Generate song lyrics from an N-gram language model')

    arg_parser.add_argument('lyrics_files', nargs='+', help=('One or more '
            'text files containing lyrics of a song, with each line separated '
            'by \\n and each verse separated by a blank line; or directories '
            'containing such files'))

    arg_parser.add_argument('-n', '--ngram-size', action='store',
            type=positive_int, default=2, help=('Specify the maximum N-gram '
            'size to use when processing lyrics and generating the song. Note '
            'that preprocessed lyrics data might not contain N-gram data up '
            'to the specified size. Default: 2'))

    arg_parser.add_argument('-p', '--preprocessed-data', action='store_true',
            help=('Use input files containing string representations of '
            'preprocessed data dictionaries instead of raw lyrics. Each input '
            'file should contain repr(d) for a single data dictionary d of '
            'the form generated by process.py.'))

    arg_parser.add_argument('-r', '--recursive', action='store_true',
            help='Recursively search input directories for files')

    arg_parser.add_argument('-s', '--section-titles', action='store_true',
            help=('Print the section title in brackets before each section of '
            'the song'))

    arg_parser.add_argument('-f', '--song-form', action='store', nargs='+',
            type=str, default=COMMON_POP_SONG_STRUCTURE, help=('Specify the '
            'structure of the song by listing the section titles as '
            'arguments. Identical titles represent sections that should be '
            'identical. Default: %s') % COMMON_POP_SONG_STRUCTURE,
            metavar='SONG_SECTION')

    return arg_parser.parse_args()

def positive_int(string):
    '''Convert a string to a positive int.

    A value for the type argument of argparse.ArgumentParser.add_argument. If
    not possible to convert, throws ArgumentTypeError'''
    try:
        i = int(string)
        if i > 0:
            return i
        else:
            raise argparse.ArgumentTypeError(N_GRAM_SIZE_INVALID_MESSAGE)
    except ValueError:
        raise argparse.ArgumentTypeError(N_GRAM_SIZE_INVALID_MESSAGE)

def sample_from_frequencies(frequencies):
    '''Sample a random choice according to the distribution in frequencies.

    We need to check for the last index, in case the probabilities actually sum
    to less than 1. This can happen because of floating point rounding.
    Arguments:
    frequencies - a dictionary mapping choices to their probabilities; the
            probabilities should sum to 1
    '''
    threshold = random.random()
    total = 0
    num_choices = len(frequencies)

    for index, (choice, probability) in enumerate(frequencies.iteritems()):
        total += probability
        if total > threshold or index == num_choices - 1:
            return choice

def smart_capitalize(string):
    '''Capitalize the string correctly even if it starts with punctuation.'''
    for i in xrange(len(string)):
        if string[i].isalpha():
            return string[:i] + string[i].upper() + string[i+1:]
        elif string[i] == ' ': # Don't capitalize past first word
            break

    return string

# Generate a song
if __name__ == '__main__':
    args = get_cl_args()

    # TODO: remove below once options are implemented
    if args.preprocessed_data:
        print '-p option not supported yet'
        sys.exit(1)

    # TODO: wrap collect_files call in try and catch invalid path exception
    lyrics_texts = [process.read_file(filename) for filename in
            collect_files(args.lyrics_files, args.recursive)]
    lyrics_data = [process.collect_data(lyrics, args.ngram_size) for lyrics
            in lyrics_texts]
    aggregate_data = process.aggregate_data(lyrics_data)
    frequencies = process.lyrics_data_to_frequencies(aggregate_data)

    print create_song(frequencies, args.song_form, args.ngram_size)
