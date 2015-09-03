from collections import Counter

from nose.tools import (assert_equal, assert_not_equal, assert_true,
        assert_false, assert_is, assert_is_not, assert_is_none,
        assert_is_not_none, assert_in, assert_not_in, assert_is_instance,
        assert_not_is_instance, raises)

import tailor.process as p

class TestAddNgramDict:

    def setup(self):
        self.unigram_base = Counter({0: 1, 1: 1})
        self.unigram_add = Counter({0: 1, 2: 1})
        self.bigram_base = {0: Counter({1: 1, 2: 1}), 1: Counter({0: 1})}
        self.bigram_add = {0: Counter({1: 1, 3: 1}), 2: Counter({0: 1})}

    def test_adds_unigram_dict(self):
        p.add_ngram_dict(self.unigram_base, self.unigram_add, 1)
        expected = Counter({0: 2, 1: 1, 2: 1})
        assert_equal(self.unigram_base, expected)

    def test_adds_bigram_dict(self):
        p.add_ngram_dict(self.bigram_base, self.bigram_add, 2)
        expected = {0: Counter({1: 2, 2: 1, 3: 1}), 1: Counter({0: 1}), 2:
                Counter({0: 1})}
        assert_equal(self.bigram_base, expected)
        # Test new dict value is a copy, not an alias of the add dict
        assert_is_not(self.bigram_base[2], self.bigram_add[2])

class TestCountNgram:

    tokens = [0, 1, 2, 3]

    def setup(self):
        self.unigram_dict = Counter({0: 1, 1: 1})
        self.bigram_dict = {0: Counter({1: 1, 2: 1}), 1: Counter({2: 1,
                3: 1})}

    def test_counts_unigram(self):
        p.count_ngram(self.unigram_dict, 0, 1, self.tokens, len(self.tokens))
        expected = Counter({0: 2, 1: 1})
        assert_equal(self.unigram_dict, expected)

    def test_counts_already_seen_bigram(self):
        p.count_ngram(self.bigram_dict, 0, 2, self.tokens, len(self.tokens))
        expected = {0: Counter({1: 2, 2: 1}), 1: Counter({2: 1, 3: 1})}
        assert_equal(self.bigram_dict, expected)

    def test_counts_bigram_with_new_first_token(self):
        p.count_ngram(self.bigram_dict, 2, 2, self.tokens, len(self.tokens))
        expected = {0: Counter({1: 1, 2: 1}), 1: Counter({2: 1, 3: 1}), 2:
                Counter({3: 1})}
        assert_equal(self.bigram_dict, expected)

    def test_counts_bigram_with_start_line_token(self):
        p.count_ngram(self.bigram_dict, -1, 2, self.tokens, len(self.tokens))
        expected = {0: Counter({1: 1, 2: 1}), 1: Counter({2: 1, 3: 1}),
                p.START_LINE_TOKEN: Counter({0: 1})}
        assert_equal(self.bigram_dict, expected)

    def test_counts_bigram_with_end_line_token(self):
        p.count_ngram(self.bigram_dict, 3, 2, self.tokens, len(self.tokens))
        expected = {0: Counter({1: 1, 2: 1}), 1: Counter({2: 1, 3: 1}), 3:
                Counter({p.END_LINE_TOKEN: 1})}
        assert_equal(self.bigram_dict, expected)

class TestSmartUncapitalize:

    def test_uncapitalizes_simple_sentence(self):
        assert_equal(p.smart_uncapitalize('Uncapitalize this sentence.'),
                'uncapitalize this sentence.')

    def test_does_not_uncapitalize_rest_of_sentence(self):
        assert_equal(p.smart_uncapitalize('Uncapitalize this Sentence.'),
                'uncapitalize this Sentence.')

    def test_does_not_uncapitalize_i(self):
        assert_equal(p.smart_uncapitalize('I will not eat cereal for lunch.'),
                'I will not eat cereal for lunch.')

    def test_does_not_uncapitalize_i_contraction(self):
        assert_equal(p.smart_uncapitalize("I'll not eat cereal for lunch."),
                "I'll not eat cereal for lunch.")

    def test_does_not_uncapitalize_beyond_first_word(self):
        assert_equal(p.smart_uncapitalize('15:00 London time.'),
                '15:00 London time.')

class TestTokenize:

    def test_separates_simple_words_with_whitespace(self):
        assert_equal(p.tokenize('Separate these   words\tinto tokens'),
                ['Separate', 'these', 'words', 'into', 'tokens'])

    def test_captures_contractions_as_single_tokens(self):
        assert_equal(p.tokenize("I'll see you"), ["I'll", 'see', 'you'])

    def test_captures_hyphenated_words_as_single_tokens(self):
        assert_equal(p.tokenize('Correctly-tokenized hyphenated words'),
                ['Correctly-tokenized', 'hyphenated', 'words'])

    def test_captures_digital_times_as_single_tokens(self):
        assert_equal(p.tokenize('The time is 19:15'),
                ['The', 'time', 'is', '19:15'])

    def test_treats_punctuation_as_separate_tokens(self):
        assert_equal(p.tokenize('Punctuation: which?? Commas, semicolons; '
                'periods. Dashes - as hyphens - and exclamation! Ellipsis...'),
                ['Punctuation', ':', 'which', '??', 'Commas', ',',
                'semicolons', ';', 'periods', '.', 'Dashes', '-', 'as',
                'hyphens', '-', 'and', 'exclamation', '!', 'Ellipsis', '...'])

    def test_ignores_parenthesized_parts(self):
        assert_equal(p.tokenize('Hey (hey) look at that (look at that)'),
                ['Hey', 'look', 'at', 'that'])

    def test_replaces_double_single_quote_with_double_quote(self):
        assert_equal(p.tokenize("''This is a quote''"),
                ['"', 'This', 'is', 'a', 'quote', '"'])
