# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import sys

class SingleBeatLog(object):
    """
    Simple wrapper around logging
    """

    def __init__(self, level=logging.INFO, filename=None):
        basicConfig = {"level":level,
            "format":'%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            "datefmt":'%m-%d %H:%M'}
        if filename:
            basicConfig['filename'] = filename
        else:
            basicConfig['stream'] = sys.stdout
        logging.basicConfig(**basicConfig)
        self.logger = logging.getLogger('singlebeat')
