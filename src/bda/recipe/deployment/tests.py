import tempfile
import unittest
import interlude
import zope.component
from pprint import pprint
from zope.testing import doctest
from zope.configuration.xmlconfig import XMLConfig

optionflags = doctest.NORMALIZE_WHITESPACE |\
    doctest.ELLIPSIS |\
    doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'common.rst',
    'svn.rst',
    'git.rst',
    'main.rst',
]

tempdir = tempfile.mkdtemp()


def test_suite():
    XMLConfig('meta.zcml', zope.component)()
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file,
            optionflags=optionflags,
            globs={
                'pprint': pprint,
                'tempdir': tempdir,
                'interact': interlude.interact
            },
        ) for file in TESTFILES
    ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
