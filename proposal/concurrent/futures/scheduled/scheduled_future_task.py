from concurrent.futures._base import PENDING

from proposal.concurrent.futures.scheduled.scheduled_future import ScheduledFuture


class ScheduledFutureTaskEntry(object):
    """
    Tuple of the internal future parameters.
    """

    def __init__(self, trigger_time: float, period: float, sequence_number: int, future: ScheduledFuture) -> None:
        super().__init__()
        self.trigger_time = trigger_time
        self.period = period
        self.sequence_number = sequence_number
        self.future = future


class ScheduledFutureTask(object):
    """
    Basic task for ScheduleThreadPoolExecutor
    """

    def __init__(self,
                 entry: ScheduledFutureTaskEntry,
                 fn, args, kwargs):
        """
        entry is a tuple of the internal feature parameters:


        Period for repeating tasks
         * A positive value indicates fixed-rate execution.
         * A negative value indicates fixed-delay execution.
         * A value of 0 indicates a non-repeating (one-shot) task.
        """
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        self.future = entry.future

        self.sequence_number = entry.sequence_number
        self.time = entry.trigger_time
        self.period = entry.period
        self.heap_index = 0
        self.outer_task = None

        self._refresh_future(entry.trigger_time, entry.period)

    def _refresh_future(self, trigger_time: float, period: float):
        # adjust scheduled time
        self.future.time = trigger_time
        # sync period value with scheduled future
        self.future.period = period

        # reset state instead recreate future, reason: memory issues
        self.future._state = PENDING

    def __eq__(self, other: object) -> bool:
        return other and self.sequence_number == other.sequence_number

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: object) -> bool:
        """ Return self<=value. """
        return other and self.__eq__(other) or self.__lt__(other)

    def __lt__(self, other: object) -> bool:
        """ Return self<value. """
        return other and self.time < other.time or (self.time == other.time
                                                    if self.sequence_number < other.sequence_number else False)

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            self.future.set_exception(exc)
            # Break a reference cycle with the exception 'exc'
            self = None
        else:
            self.future.set_result(result)
