# TODO List

## Bug Fixes

- Add testing
- Make sure all docstrings use 3rd person declarative (after ngrams is merged)
- Handle invalid paths with an exception
- Fix I/i collection - being counted separately when I is first or in middle of
  line
- Fix naive joining of tokens (' '.join) to account for punctuation
- Preserve capitalization of names

## Features
- Auto-generation of README.md with updated Usage section (on commit)
- Abstract hard-coded unigram and bigram collection and generation to arbitrary
  n-gram
- Allow user to specify n-gram config (default: bigram, or based on source data
  size?)
- Implement -p (preprocessed data) input mode
- Add line length tuning to prevent very short and very long lines
  * To avoid very short, after sampling bigram and getting <END>, actually end
    with probability taken from tokens_per_line at current length, else
    resample from bigram (CAVEAT: if <END> prob is 100%, can't use loop or will
    get stuck)
  * How to avoid long lines? May not be necessary, doesn't happen too often,
    and may happen even less with more source data
- Try higher n-grams with linear interpolation or backoff to improve coherency
- Title generation
- Let user specify -i option to automatically retrieve songs via
  search on metrolyrics (need to write scrape.py module for this)
