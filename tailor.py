from sys import argv
import random
import process
from process import BIGRAMS, LINES_PER_VERSE, TOKENS_PER_LINE
from process import START_LINE_TOKEN, END_LINE_TOKEN

COMMON_POP_SONG_STRUCTURE = ['Verse 1', 'Chorus', 'Verse 2', 'Chorus',
  'Bridge', 'Chorus']

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

  return '\n'.join(lines) + '\n'

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

  return '\n'.join(['[%s]\n' % section + song_parts[section] for section in
      structure])

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

# Create a song based on a given lyrics file
if __name__ == '__main__':
  if len(argv) != 2:
    print 'Usage: python tailor.py lyrics_filename'

  else:
    with open(argv[1]) as lyrics_file:
      lyrics = lyrics_file.read()

    frequencies = process.compute_frequencies(process.collect_data(lyrics))
    print create_song(frequencies, COMMON_POP_SONG_STRUCTURE)
