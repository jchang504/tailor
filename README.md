# Tailor

Tailor is a Python command-line tool for automatic generation of "original"
song lyrics based on a collection of songs' lyrics.

The current version supports multiple file and directory (with optional
recursive search) input, uses a bigram-based language model to generate the
lyrics, and outputs to stdout. There are a lot more cool features to come,
being added faster than I can implement them to [`TODO.md`](/TODO.md)!

## Usage

```
usage: tailor.py [-h] [-n N_GRAM_SIZE] [-p] [-r] [-s] [-f SONG_FORM]
                 lyrics_files [lyrics_files ...]

Generate song lyrics from an N-gram language model

positional arguments:
  lyrics_files          One or more text files containing lyrics of a song,
                        with each line separated by \n and each verse
                        separated by a blank line; or directories containing
                        such files

optional arguments:
  -h, --help            show this help message and exit
  -n N_GRAM_SIZE, --n-gram-size N_GRAM_SIZE
                        Specify the maximum N-gram size to use when processing
                        lyrics and generating the song. Note that preprocessed
                        lyrics data might not contain N-gram data up to the
                        specified size. Default: 2
  -p, --preprocessed-data
  -r, --recursive
  -s, --section-titles
  -f SONG_FORM, --song-form SONG_FORM
```

## Thanks

Thanks to the eponymous Taylor Swift, whose critics' claims that all her songs
are about the same thing gave me the idea for this.

Also thanks to www.metrolyrics.com, which provided the lyrics for testing and
development.

Lastly, the greatest thanks to Ro-IT, a constant source of technical and
general support, advice, and assistance. "Stay, stay, pay."
