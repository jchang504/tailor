# Tailor

Tailor is a Python command-line tool for automatic generation of "original",
"creative" songs based on a single or collection of songs.

This is a first draft, the result of ~12 hours of hacking. It only supports
offline, single song input, bigram-based song generation. But see
[`TODO.md`](/TODO.md) for upcoming features!

## Usage

```
python tailor.py lyrics_filename
```

`lyrics_filename` should be the name of a text file containing the lyrics to a
song, with lines separated by `'\n'` and verses separated by a blank line.

## Thanks

Thanks to the eponymous Taylor Swift, whose critics' claims that all her songs
are about the same thing gave me the idea for this.

Also thanks to www.metrolyrics.com, which provided the lyrics for testing and
development.

Lastly, the greatest thanks to Ro-IT, a constant source of technical and
general support, advice, and assistance. "Stay, stay, pay."
