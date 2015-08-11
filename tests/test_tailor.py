'''A module for testing attributes of the entire project.'''

import importlib
from nose.tools import assert_is_not_none

class TestDocumentationCompleteness:

    @classmethod
    def setup_class(cls):
        import tailor
        cls.modules = {name: importlib.import_module('tailor.' + name) for name
                in tailor.__all__}

    @staticmethod
    def check_has_docstring(obj, name):
        assert_is_not_none(obj.__doc__, '%s has no docstring' % name)

    def test_all_modules_documented(self):
        for name, module in self.modules.iteritems():
            yield (self.check_has_docstring, module, name)

    def test_all_functions_documented(self):
        for _, module in self.modules.iteritems():
            for name, attr in module.__dict__.iteritems():
                if callable(attr):
                    yield (self.check_has_docstring, attr, name)
