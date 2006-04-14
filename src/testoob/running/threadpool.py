# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2006 The TestOOB Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Supply a ThreadPool, dispatching work to different threads.
"""

import sys
import threading
import Queue


class Error(Exception):
    """ General threadpool error """

class _DismissalLetter:
    """ Sent to a worker thread to dismiss it """
    

class ThreadPool(object):
    """ I'm a simple thread pool using constant size.

    To run a function in a thread, call dispatch() with a callable and
    optional arguments and keywords. callable must be thread safe!
    
    Usage::

        p = ThreadPool(10)
        p.start()
        try:
            p.dispatch(callable, foo, bar="baz")
            ...
        finally:
            p.stop()

    The pool keeps a constant number of worker threads active while its
    running, and dismiss all of them when you stop it. The pool can be
    stopped and started as needed. Before exiting the application, the
    pool must be stopped. Use try finally to make sure your app will
    quit.

    You can resize the pool while its running by modifying the size
    attribute.

    Unhandled exceptions in code executed by worker threads are printed
    to the pool logFile, defaulting to sys.stderr.

    The pool itself is NOT thread safe, and should be accessed by only
    one thread.
    """

    # ------------------------------------------------------------------
    # Initialization
    
    def __init__(self, size=10, logFile=None):
        """ Initialize a pool
        
        @param size: number of threads to employ.
        @param logFile: where exceptions go (default to sys.stderr)
        """
        self._queue = Queue.Queue()

        # Safe worker threads so we can join them later when we stop
        self._workers = []
        
        self._running = False
        self.setSize(size)
        self.logFile = logFile or sys.stderr

    # ------------------------------------------------------------------
    # Running
        
    def start(self):
        """ Start a pool with size worker threads.

        Raise threadpool.Error if the pool is already running.
        """
        if self._running:
            raise Error("the pool is already running.")
        
        for worker in range(self._size):
            self._employWorker()
        self._running = True
        
    def stop(self):
        """ Stop a pool. All workers are dismissed.

        Will block until all the workers finished their assignment,
        which can take some time.

        Raise threadpool.Error if the pool is not running.
        """
        if not self._running:
            raise Error("the pool is not running.")

        workers = self._workers[:]
        for worker in workers:
            self._dismissWorker()
        for worker in workers:
            worker.join()
                    
        self._running = False
        
    # ------------------------------------------------------------------
    # Dispatching

    def dispatch(self, callable, *args, **kw):
        """ Add callable to the work queue.

        Raise threadpool.Error if the pool is not running.

        @param callable: a callable
        @param args: arguments for callable
        @param kw: keyword arguments for callable
        """
        if not self._running:
            raise Error("the pool is not running.")

        self._queue.put((callable, args, kw))
            
    # ------------------------------------------------------------------
    # Accessing

    running = property(lambda self: self._running)

    def setSize(self, count):
        assert count >= 1, "at least one worker threads must be employed"
        self._size = count
        if self._running:
            self.stop()
            self.start()

    size = property(lambda self: self._size, setSize,
                    doc="number of worker threads")

    workers = property(lambda self: len(self._workers))

    def queueEmpty(self):
        """ Return True if the queue is empty, False otherwise.

        Because of multithreading semantics, this is not reliable.
        """
        return self._queue.empty()
        
    # ------------------------------------------------------------------
    # Private

    def _workerMainLoop(self):
        """ Loop forever, trying to get work from, the queue. """
        me = threading.currentThread()
        while 1:
            callable, args, kw = self._queue.get()
            if callable is _DismissalLetter:
                break            
            try:
                callable(*args, **kw)
            except:
                import traceback
                traceback.print_exc(file=self.logFile)
            del callable, args, kw

        self._workers.remove(me)
            
    def _employWorker(self):
        t = threading.Thread(target=self._workerMainLoop)
        self._workers.append(t)
        t.start()
        
    def _dismissWorker(self):
        """ Dismiss the unfortunate next waiting worker """
        self.dispatch(_DismissalLetter)
