import time
from concurrent.futures._base import Future
from unittest import TestCase

from proposal.concurrent.futures.scheduled.scheduled_thread_pool_executor import ScheduledThreadPoolExecutor


class AssertCondition(object):

    def __init__(self) -> None:
        super().__init__()
        self.completable_feature = Future()
        self.test_count = 0
        self.test_method = self.test
        self.test_method_with_sleep = self.test_with_sleep

    def test(self, max_count):
        print('Next count: {test_count}'.format(test_count=self.test_count))
        self.test_count += 1
        if self.test_count >= max_count:
            self.completable_feature.set_result(self.test_count)
            self.completable_feature.done()

    def test_with_sleep(self, max_count, sleep_time):
        self.test(max_count)
        time.sleep(sleep_time)

    def result(self):
        return self.completable_feature.result()


class TestScheduledThreadPoolExecutor(TestCase):

    def test_schedule(self):
        with ScheduledThreadPoolExecutor(max_workers=1) as executor:
            start_time = time.time()
            self.assertEqual(executor.schedule(0.2, max, 1, 2).result(), 2)
            delay = time.time() - start_time
            self.assertTrue(delay > 0.2)

    def test_schedule_at_fixed_rate(self):
        with ScheduledThreadPoolExecutor(max_workers=1) as executor:
            start_time = time.time()
            assert_condition = AssertCondition()
            periodic_future = executor.schedule_at_fixed_rate(0.2, 0.2, assert_condition.test_method, 2)
            self.assertTrue(periodic_future.is_periodic())
            self.assertEqual(assert_condition.result(), 2)
            delay = time.time() - start_time
            self.assertTrue(delay > 0.4)

    def test_schedule_at_fixed_delay(self):
        with ScheduledThreadPoolExecutor(max_workers=1) as executor:
            start_time = time.time()
            assert_condition = AssertCondition()
            periodic_future1 = executor.schedule_with_fixed_delay(0.2, 0.2,
                                                                  assert_condition.test_method_with_sleep, 2, 0.2)
            self.assertTrue(periodic_future1.is_periodic())
            self.assertEqual(assert_condition.result(), 2)
            delay = time.time() - start_time
            self.assertTrue(delay > 0.5)

    def test_shutdown(self):
        with ScheduledThreadPoolExecutor(max_workers=1) as executor:
            start_time = time.time()
            assert_condition = AssertCondition()
            periodic_future1 = executor.schedule_with_fixed_delay(0.2, 0.2,
                                                                  assert_condition.test_method_with_sleep, 2, 0.2)
            self.assertTrue(periodic_future1.is_periodic())
            self.assertEqual(assert_condition.result(), 2)

            # SHUTDOWN POOL
            executor.shutdown()

            delay = time.time() - start_time
            self.assertTrue(delay > 0.5)
            self.assertTrue(delay < 1)

    def test_submit(self):
        with ScheduledThreadPoolExecutor(max_workers=1) as executor:
            start_time = time.time()
            assert_condition = AssertCondition()
            executor.submit(assert_condition.test_method_with_sleep, 1, 0.2)
            last_future = executor.submit(assert_condition.test_method_with_sleep, 1, 0.2)

            last_future.result()
            delay = time.time() - start_time
            self.assertTrue(delay > 0.4)
