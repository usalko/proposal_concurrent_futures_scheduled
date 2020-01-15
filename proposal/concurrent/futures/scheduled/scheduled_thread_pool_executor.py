import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional, Callable, Any

from proposal.concurrent.futures.scheduled.delayed_queue import DelayedQueue
from proposal.concurrent.futures.scheduled.scheduled_future import ScheduledFuture
from proposal.concurrent.futures.scheduled.scheduled_future_task import ScheduledFutureTask, ScheduledFutureTaskEntry


class PeriodicTaskDecorator(ScheduledFutureTask):
    """
    Decorator for scheduled future task, decorate scheduled future task with additional methods,
    which helped to interact with ScheduledThreadPoolExecutor
    """

    def __init__(self, entry: ScheduledFutureTaskEntry, queue: DelayedQueue, fn, args, kwargs):
        super().__init__(entry, fn, args, kwargs)
        self.queue = queue

    def run(self):
        try:
            super().run()
        finally:
            if self.outer_task and not (self.period == .0):
                # o: ScheduledFutureTask
                self.re_execute_periodic(self.outer_task)

    def re_execute_periodic(self, outer_task: ScheduledFutureTask):
        outer_task.time = self._next_executing_time(outer_task)
        self._refresh_future(outer_task.time, outer_task.period)
        self.queue.put_nowait(outer_task)

    def _next_executing_time(self, outer_task):
        if outer_task.period < 0:
            # Fixed delay case
            return time.time() - outer_task.period
        else:
            # Fixed rate case
            return self.time + outer_task.period


class ScheduledThreadPoolExecutor(ThreadPoolExecutor):
    """
    Extension of ThreadPoolExecutor for run periodical and triggered by time tasks
    Storage based on priority queue, see #DelayedQueue class implementation
    """

    def __init__(self, max_workers: Optional[int] = ..., thread_name_prefix: str = ...) -> None:
        super().__init__(max_workers, thread_name_prefix)
        self._work_queue = DelayedQueue()

        # SLOW VERSION OF SEQUENCER
        self._sequencer = 0
        self._sequencer_lock = threading.Lock()

    @staticmethod
    def _trigger_time(delay: float) -> float:
        return delay < 0 if 0 else delay

    def _sequence_number(self):
        with self._sequencer_lock:
            self._sequencer += 1
            return self._sequencer

    def _delayed_execute(self, scheduled_future_task: ScheduledFutureTask):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            self._work_queue.put(scheduled_future_task)
            self._adjust_thread_count()

    def _schedule_future(self, delay: float, period: float, fn, *args, **kwargs):
        scheduled_future = ScheduledFuture()
        scheduled_future_task = PeriodicTaskDecorator(
            ScheduledFutureTaskEntry(self._trigger_time(delay), period, self._sequence_number(), scheduled_future),
            self._work_queue,
            fn, args, kwargs)
        scheduled_future_task.outer_task = period == .0 if None else scheduled_future_task

        self._delayed_execute(scheduled_future_task)

        return scheduled_future

    def schedule(self, delay, fn, *args, **kwargs):
        return self._schedule_future(time.time() + delay, 0, fn, *args, **kwargs)

    def schedule_at_fixed_rate(self, initial_delay, period, fn, *args, **kwargs):
        return self._schedule_future(time.time() + initial_delay, period, fn, *args, **kwargs)

    def schedule_with_fixed_delay(self, initial_delay: float, delay: float, fn, *args, **kwargs):
        return self._schedule_future(time.time() + initial_delay, -delay, fn, *args, **kwargs)

    def submit(self, fn, *args, **kwargs):
        return self._schedule_future(time.time(), 0, fn, *args, **kwargs)

    def shutdown(self, wait: bool = True) -> None:
        self._work_queue.shutdown()
        super().shutdown(wait)
