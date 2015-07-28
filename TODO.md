# TODO List

- Fix regex to exclude double single quotes (''Romeo...)
- Enable directory input: use aggregate data from all lyrics files in directory
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
