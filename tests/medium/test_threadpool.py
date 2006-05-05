"threadpool tests"

import sys
import time
import testoob
from testoob.running import threadpool
import testoob.testing as tt

from unittest import TestCase
class BaseTestCase(TestCase):

    size = 10
    workoutIterations = 1000

    def setUp(self):
        self.pool = threadpool.ThreadPool(self.size)

    def tearDown(self):
        if self.pool.running:
            self.pool.stop()
        del self.pool

    def workout(self):
        def job():
            pass
        for i in range(self.workoutIterations):
            self.pool.dispatch(job)

class creation(BaseTestCase):

    def test_size(self):
        self.assertEqual(self.pool.size, self.size)

    def test_is_not_running(self):
        self.failIf(self.pool.running)

    def test_dont_employ_workers(self):
        self.assertEqual(self.pool.workers, 0)

    def test_logFile(self):
        self.assert_(self.pool.logFile is sys.stderr)

    def test_stop_raises(self):
        tt.assert_raises(threadpool.Error, self.pool.stop)

    def test_dispatch_raises(self):
        tt.assert_raises(threadpool.Error, self.pool.dispatch,
                         lambda: "foo")


class start(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.pool.start()

    def test_is_running(self):
        self.assert_(self.pool.running)

    def test_start_raises(self):
        tt.assert_raises(threadpool.Error, self.pool.start)

    def test_employ_all_workers(self):
        self.assertEqual(self.pool.workers, self.pool.size)

class workout(BaseTestCase):

    workoutIterations = 100

    def setUp(self):
        BaseTestCase.setUp(self)
        self.results = []
        self.pool.start()
        self.workout()

    def workout(self):
        for i in range(self.workoutIterations):
            # list.append is thread safe
            self.pool.dispatch(self.results.append, 'ok')

    def test_is_running(self):
        self.assert_(self.pool.running)

    def test_employ_all_workers(self):
        self.assertEqual(self.pool.workers, self.pool.size)

    def test_work_done(self):
        while 1:
            time.sleep(0.01)
            if self.pool.queueEmpty():
                break
        self.assertEqual(self.results, ['ok'] * self.workoutIterations)

class stop(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.pool.start()
        self.workout()
        self.pool.stop()

    def test_is_not_running(self):
        self.failIf(self.pool.running)

    def test_stop_raises(self):
        tt.assert_raises(threadpool.Error, self.pool.stop)

    def test_dispatch_raises(self):
        tt.assert_raises(threadpool.Error, self.pool.dispatch,
                         lambda: "foo")

    def test_dismiss_all_workers(self):
        self.assertEqual(self.pool.workers, 0)

class restart(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.pool.start()
        self.workout()
        self.pool.stop()
        self.pool.start()

    def test_is_running(self):
        self.assert_(self.pool.running)

    def test_employ_all_workers(self):
        self.assertEqual(self.pool.workers, self.pool.size)

class resize(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.pool.start()

    def check_resize(self, count):
        self.pool.size = count
        self.workout()
        self.assertEqual(self.pool.workers, count)

    def test_shrink_idle(self):
        self.check_resize(5)

    def test_grow_idle(self):
        self.check_resize(50)

    def test_shrink_with_load(self):
        self.workout()
        self.check_resize(5)

    def test_grow_with_load(self):
        self.workout()
        self.check_resize(50)

if __name__ == "__main__":
    testoob.main()
