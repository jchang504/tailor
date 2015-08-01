# TODO List

- Finish usage help messages for options and abstract arg processing to
  function
- Fix I/i collection - being counted separately when I is first or in middle of
  line
- Fix regex to exclude double single quotes (''Romeo...)
- Fix naive joining of tokens (' '.join) to account for punctuation
- Abstract hard-coded unigram and bigram collection to arbitrary n-gram
- Have two input modes: either raw lyrics (unprocessed) or output of process.py
- Add options, let user specify -i option to automatically retrieve songs via
  search on metrolyrics (need to write scrape.py module for this)
- Add line length tuning to prevent very short and very long lines
  * To avoid very short, after sampling bigram and getting <END>, actually end
    with probability taken from tokens_per_line at current length, else
    resample from bigram (CAVEAT: if <END> prob is 100%, can't use loop or will
    get stuck)
  * How to avoid long lines? May not be necessary, doesn't happen too often,
    and may happen even less with more source data
- Allow user to specify n-gram config (default: bigram, or based on source data
  size?)
  * Try linear interpolation or backoff
- Allow user to specify song structure
