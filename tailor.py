import argparse
import os
import random
import sys

import process
from process import BIGRAMS, LINES_PER_VERSE, TOKENS_PER_LINE
from process import START_LINE_TOKEN, END_LINE_TOKEN

COMMON_POP_SONG_STRUCTURE = ['Verse 1', 'Chorus', 'Verse 2', 'Chorus',
        'Bridge', 'Chorus']
N_GRAM_SIZE_INVALID_MESSAGE = 'N-gram size must be a positive integer'

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
            if args.recursive:
                for root, dirs, files, in os.walk(path):
                    files_list += [os.path.join(root, f) for f in files]
            else:
                pathnames = [os.path.join(path, name) for name in
                        os.listdir(path)]
                files_list += filter(os.path.isfile, pathnames)

    return files_list

def create_line(bigram_frequencies):
    '''Creates a line of a song.

    Arguments:
    bigram_frequencies - a bigram frequency mapping of the form generated in
            process.py
    '''
    tokens = []
    token = sample_from_frequencies(bigram_frequencies[START_LINE_TOKEN])

    while token != END_LINE_TOKEN: # Let probability determine line length
        tokens.append(token)
        token = sample_from_frequencies(bigram_frequencies[token])

    return smart_capitalize(' '.join(tokens))

def create_section(bigram_frequencies, num_lines):
    '''Creates a section of a song num_lines long.

    Arguments:
    bigram_frequencies - a bigram frequency mapping of the form generated in
            process.py
    tokens_per_line_frequencies - maps length of a line (in tokens) to
            frequency of this length
    '''
    lines = []
    for i in xrange(num_lines):
        lines.append(create_line(bigram_frequencies))

    return '\n'.join(lines)

def create_song(frequency_data, structure):
    '''Create a song with a specified structure from the frequency_data.

    Arguments:
    frequency_data - a data dictionary of the form returned by
            process.py:collect_data
    structure - a list of strings representing the sections of the song;
            identical strings represent repeated sections (e.g. choruses)
    '''
    lpv_frequencies = frequency_data[LINES_PER_VERSE]
    song_parts = {}

    for section in structure:
        if section not in song_parts:
            song_parts[section] = create_section(frequency_data[BIGRAMS], 
                    sample_from_frequencies(lpv_frequencies))

    return '\n\n'.join(['[%s]\n%s' % (section, song_parts[section]) for section
            in structure])

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
        raise argparse.ArgumentTypeError(N_GRAM_SIZE_NOT_POSITIVE_MESSAGE)

def read_file(filename):
    '''Read the full text of a file.'''
    with open(filename) as f:
        return f.read()

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

    # Configure command line arguments
    # TODO: finish help messages; separate into function
    arg_parser = argparse.ArgumentParser(
            description='Generate song lyrics from an N-gram language model')
    arg_parser.add_argument('lyrics_files', nargs='+', help=('One or more '
            'text files containing lyrics of a song, with each line separated '
            'by \\n and each verse separated by a blank line; or directories '
            'containing such files'))
    arg_parser.add_argument('-n', '--n-gram-size', action='store',
            type=positive_int, default=2, help=('Specify the maximum N-gram '
            'size to use when processing lyrics and generating the song. Note '
            'that preprocessed lyrics data might not contain N-gram data up '
            'to the specified size. Default: 2'))
    arg_parser.add_argument('-p', '--preprocessed-data', action='store_true')
    arg_parser.add_argument('-r', '--recursive', action='store_true')
    arg_parser.add_argument('-s', '--section-titles', action='store_true')
    arg_parser.add_argument('-f', '--song-form', action='store', nargs=1,
            default=COMMON_POP_SONG_STRUCTURE)
            # TODO: figure out best way to input structure here (use type=)

    args = arg_parser.parse_args()

    # TODO: remove below once options are implemented
    if (args.preprocessed_data or
            args.n_gram_size != 2 or
            args.song_form != COMMON_POP_SONG_STRUCTURE):
        print '-n, -p, -f options not supported yet'
        sys.exit(1)

    lyrics_texts = [read_file(filename) for filename in
            collect_files(args.lyrics_files, False)]
    lyrics_data = [process.collect_data(lyrics) for lyrics in lyrics_texts]
    aggregate_data = process.aggregate_data(lyrics_data)
    frequencies = process.compute_frequencies(aggregate_data)
            
    print create_song(frequencies, COMMON_POP_SONG_STRUCTURE)
