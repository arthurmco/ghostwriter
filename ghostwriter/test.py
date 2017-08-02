#
#   Ghostwriter test suite
#
#   Copyright (C) 2017 Arthur M
#

import unittest
from ghostwriter import app, mm
from ghostwriter.ghtest import *
import sys

if __name__ == '__main__':
    try:
        testsuite = unittest.TestLoader().discover('./ghostwriter/ghtest')
    except:
        testsuite = unittest.TestLoader().discover('./ghtest')

    runner = unittest.TextTestRunner(verbosity=2)
    ret = not runner.run(testsuite).wasSuccessful()
    sys.exit(ret)


