# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 The TestOOB Team
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

"The proxy used as a result object for PyUnit suites"

def ObserverProxy(method_names):
    """
	Create a thread-safe proxy that forwards methods to a group of observers.
	Each method can return a boolean value, the proxy will return the '&'
	between them.
    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413701.
    """
    class Proxy:
        def __init__(self):
            self.observers = []
            import threading
            self.lock = threading.RLock()
        def add_observer(self, observer):
            self.observers.append(observer)
        def remove_observer(self, observer):
            self.observers.remove(observer)

    def create_method_proxy(method_name):
        def method_proxy(self, *args, **kwargs):
            self.lock.acquire()
            retVal = True
            try:
                for observer in self.observers:
                    retVal &= bool(getattr(observer, method_name)(*args, **kwargs))
            finally:
                self.lock.release()
            return retVal
        return method_proxy

    for method_name in method_names:
        setattr(Proxy, method_name, create_method_proxy(method_name))

    return Proxy

ReporterProxy = ObserverProxy([
    "start",
    "done",
    "startTest",
    "stopTest",
    "addError",
    "addFailure",
    "addSuccess",
    "addAssert",
    "isSuccessful",
])


