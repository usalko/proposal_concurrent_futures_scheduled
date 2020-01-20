#!/usr/bin/env python
__author_1__ = 'Ivan Usalko'
__author__ = __author_1__
__copyright__ = 'Copyright 2020, proposal_concurrent_futures_scheduled'
__credits__ = [__author_1__]
__license__ = 'Apache 2.0'
__version__ = '1.0.2'
__maintainer__ = __author_1__
__email__ = 'ivict@rambler.ru'
__status__ = 'Production'

import time
from concurrent.futures._base import Future


class ScheduledFuture(Future):
    """
    Future with additional internal parameters
    """

    time = .0
    period = .0

    def get_delay(self) -> float:
        """
        Get remaining delay in seconds (float value),
        zero or negative values indicate that the delay has already elapsed.
        """
        return self.time - time.time()

    def is_periodic(self) -> float:
        """
        Returns True if this is a periodic (not a one-shot) action.
        """
        return self.period != 0
