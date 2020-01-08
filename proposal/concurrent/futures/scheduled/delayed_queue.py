import threading
from queue import PriorityQueue

from proposal.concurrent.futures.scheduled.scheduled_future import ScheduledFuture
from proposal.concurrent.futures.scheduled.scheduled_future_task import ScheduledFutureTask, ScheduledFutureTaskEntry

FINISH_TASK_FUTURE = ScheduledFuture()
FINISH_TASK_FUTURE.cancel()
FINISH_TASK = ScheduledFutureTask(ScheduledFutureTaskEntry(0, 0, 0, FINISH_TASK_FUTURE), max, (1, 2), {})


class DelayedQueue(PriorityQueue):
    """
    Specific tasks storage for ScheduledThreadPoolExecutor,
    implementation based on PriorityQueue
    """

    def __init__(self, maxsize: int = 16) -> None:
        super().__init__(maxsize)
        # Thread designated to wait for the task at the head of the
        # queue.  This variant of the Leader-Follower pattern
        # (http://www.cs.wustl.edu/~schmidt/POSA/POSA2/)
        self.leader = None

        self.lock = threading.RLock()
        # Condition signalled when a newer task becomes available at the
        # head of the queue or a new thread may need to become leader.
        self.available = threading.Condition(self.lock)

    def _get(self) -> object:
        with self.lock:
            try:
                if self._qsize() == 0:
                    self.available.wait()

                task = super()._get()
                if task == FINISH_TASK:
                    return None

                delay = task.future.get_delay()
                if delay > .0:
                    if self.leader:
                        self.available.wait()
                    else:
                        self.leader = threading.current_thread()
                        try:
                            self.available.wait(delay)
                        finally:
                            if self.leader == threading.current_thread():
                                self.leader = None

                return task
            finally:
                if not self.leader and self._qsize() > 0:
                    self.available.notify_all()

    def _put(self, item: object) -> None:
        with self.lock:
            try:
                if not item:
                    super()._put(FINISH_TASK)
                    return
                super()._put(item)
            finally:
                self.available.notify_all()

    def shutdown(self) -> None:
        """
        Notify all waiters for shutdown signal
        """
        with self.lock:
            self.available.notify_all()
