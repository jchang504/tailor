'''Process raw lyrics text files into dictionaries containing all the data
needed to generate new songs.
'''
import re
from collections import Counter

# Regexes for tokenization
CONTRACTION_OR_HYPHENATED_WORD_PATTERN = r"(?:\w+['-]\w+)"
DIGITAL_TIME_PATTERN = r'(?:\d{1,2}:\d{2})'
SIMPLE_WORD_PATTERN = r'(?:\w+)'
PUNCTUATION_PATTERN = r'(?:[,;:.?!"-]+)'
LYRICS_TOKEN_REGEX = re.compile('|'.join(
        [CONTRACTION_OR_HYPHENATED_WORD_PATTERN, DIGITAL_TIME_PATTERN,
        SIMPLE_WORD_PATTERN, PUNCTUATION_PATTERN]))

PAREN_PHRASES_REGEX = re.compile(r'\([^)]+\)')
START_LINE_TOKEN = '<START>'
END_LINE_TOKEN = '<END>'

# Data dictionary keys
NGRAMS = 'ngrams'
LINES_PER_VERSE = 'lpv'
TOKENS_PER_LINE = 'tpl'

def add_ngram_dict(accum_dict, add_dict, n):
    '''Add the n-gram counts in add_dict to those in accum_dict.

    Recursively walk down the nested dictionaries to add their Counters
    together properly. This mutates accum_dict but not add_dict.
    '''
    if n == 1: # At last level, dicts are Counters
        accum_dict += add_dict

    else:
        for token, next_add in add_dict.iteritems():
            next_accum = accum_dict.get(token)

            if next_accum is None:
                accum_dict[token] = (Counter if n == 2 else dict)(next_add)
            else:
                add_ngram_dict(next_accum, next_add, n-1)

def aggregate_data(lyrics_data_list):
    '''Aggregate data about multiple songs' lyrics.

    Given a list of data dictionaries of the form returned by collect_data,
    combines the data into a single dictionary of the same form by adding
    Counters together. The NGRAMS list will be truncated to the length of the
    shortest NGRAMS list among the input data.
    '''
    n = min([len(lyrics_data[NGRAMS])-1 for lyrics_data in lyrics_data_list])
    total_ngrams = [None, Counter()] + [{} for i in xrange(n-1)]
    total_lines_per_verse = Counter()
    total_tokens_per_line = Counter()

    for lyrics_data in lyrics_data_list:
        for i in xrange(1, n+1):
            add_ngram_dict(total_ngrams[i], lyrics_data[NGRAMS][i], i)

        total_lines_per_verse.update(lyrics_data[LINES_PER_VERSE])
        total_tokens_per_line.update(lyrics_data[TOKENS_PER_LINE])

    return {NGRAMS: total_ngrams, LINES_PER_VERSE: total_lines_per_verse,
            TOKENS_PER_LINE: total_tokens_per_line}

def collect_data(song_lyrics, n):
    '''Collect data about a song's lyrics.

    Arguments:
    - song_lyrics: a string containing the song's lyrics, where each line is
        separated by \n, and each verse is separated by a blank line
    - n: the maximum size n-grams to collect counts for; minimum 1
    Returns a dictionary with these keys and values:
    - NGRAMS: a list where index n contains a nested dictionary mapping n-grams
      to their counts (e.g. {'a': {'trigram': {'dictionary': 1} } }); index 0
      is None
    - LINES_PER_VERSE: a Counter representing the distribution of verse lengths
    - TOKENS_PER_LINE: a Counter representing the distribution of line lengths
    '''
    ngrams = [None, Counter()] + [{} for i in xrange(n-1)]
    lines_per_verse = Counter()
    tokens_per_line = Counter()

    current_lines = 0
    for line in song_lyrics.splitlines():
        uncap_line = smart_uncapitalize(line)
        tokens = tokenize(uncap_line) # Avoid distinguishing first word of line
        len_tokens = len(tokens)

        if len_tokens > 0:
            for size in xrange(1, n+1):
                for i in xrange(1-size, len_tokens):
                    count_ngram(ngrams[size], i, size, tokens, len_tokens)

            tokens_per_line[len_tokens] += 1
            current_lines += 1

        else: # Blank line: end of verse
            lines_per_verse[current_lines] += 1
            current_lines = 0

    return {NGRAMS: ngrams, LINES_PER_VERSE: lines_per_verse, TOKENS_PER_LINE:
            tokens_per_line}

def count_ngram(ngram_dict, i, n, tokens, len_tokens):
    '''Count the n-gram represented by tokens[i:i+n] in ngram_dict.

    Recursively walk down the nested dictionaries to count an occurrence of the
    n-gram starting at index i in tokens. Recursion is beautiful.
    '''
    if i < 0:
        token = START_LINE_TOKEN
    elif i >= len_tokens:
        token = END_LINE_TOKEN
    else:
        token = tokens[i]

    if n == 1: # At last level, ngram_dict is a Counter
        ngram_dict[token] += 1

    else:
        next_dict = ngram_dict.get(token)
        if next_dict is None: # First encounter of this token at this level
            ngram_dict[token] = next_dict = Counter() if n == 2 else {}

        count_ngram(next_dict, i+1, n-1, tokens, len_tokens)

def counter_to_frequency_dict(counter):
    '''Maps a counter to a frequency dictionary.

    The result dictionary has the same keys as the counter, but the values are
    the counts divided by the total of all counts.
    '''
    counts_total = sum(counter.values())
    frequencies = {}

    for key in counter:
        frequencies[key] = float(counter[key]) / counts_total

    return frequencies

def lyrics_data_to_frequencies(lyrics_data):
    '''Maps a lyrics data dictionary holding counts to one holding frequencies.

    Given a data dictionary of the form returned by collect_data, returns a
    data dictionary with the same keys, but counts converted to relative
    frequencies.
    '''
    n = len(lyrics_data[NGRAMS])-1
    ngram_frequencies = [None] + [ngram_counts_to_frequencies(
            lyrics_data[NGRAMS][i], i) for i in xrange(1, n+1)]

    lpv_frequencies = counter_to_frequency_dict(lyrics_data[LINES_PER_VERSE])
    tpl_frequencies = counter_to_frequency_dict(lyrics_data[TOKENS_PER_LINE])

    return {NGRAMS: ngram_frequencies, LINES_PER_VERSE: lpv_frequencies,
            TOKENS_PER_LINE: tpl_frequencies}

def ngram_counts_to_frequencies(ngram_dict, n):
    '''Maps an ngram_dict holding counts to one holding relative frequencies.

    Recursively walk down the nested dictionaries and convert the Counters at
    the last level to relative frequency dictionaries.
    '''
    if n == 1:
        return counter_to_frequency_dict(ngram_dict)

    else:
        return {token: ngram_counts_to_frequencies(next_dict, n-1) for token,
                next_dict in ngram_dict.iteritems()}

def read_file(filename):
    '''Read the full text of a file.'''
    with open(filename) as f:
        return f.read()

def smart_uncapitalize(string):
    '''Uncapitalize a string correctly even if it begins with punctuation.

    Also avoid uncapitalizing a first person subject pronoun (I, I'm, etc.).
    '''
    if string.startswith('I ') or string.startswith("I'"):
        return string

    for i in xrange(len(string)):
        if string[i].isalpha():
            return string[:i] + string[i].lower() + string[i+1:]
        elif string[i] == ' ': # Don't uncapitalize past first word
            break

    return string

def tokenize(line):
    '''Split a line into tokens.

    First remove (parenthesized phrases) and replace '' with ", then tokenize
    the rest according to a special regex sauce.
    '''
    parens_removed = PAREN_PHRASES_REGEX.sub('', line)
    double_single_quotes_replaced = parens_removed.replace("''", '"')
    return LYRICS_TOKEN_REGEX.findall(double_single_quotes_replaced)
