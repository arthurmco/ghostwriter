#
#   Ghostwriter test suite
#
#   Copyright (C) 2017 Arthur M
#

import unittest
from ghostwriter import app, mm
from ghostwriter.ghtest import *

if __name__ == '__main__':
    try:
        testsuite = unittest.TestLoader().discover('./ghostwriter/ghtest')
    except:
        testsuite = unittest.TestLoader().discover('./ghtest')

    unittest.TextTestRunner(verbosity=2).run(testsuite)


