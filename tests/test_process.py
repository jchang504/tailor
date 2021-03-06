from nose.tools import (assert_equal, assert_not_equal, assert_true,
        assert_false, assert_is, assert_is_not, assert_is_none,
        assert_is_not_none, assert_in, assert_not_in, assert_is_instance,
        assert_not_is_instance, raises)

import tailor.process as p

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
        assert_equal(p.smart_uncapitalize('15:00 is the time in London.'),
                '15:00 is the time in London.')