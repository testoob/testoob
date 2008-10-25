# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005-2008 The Testoob Team
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

class SubprocessCommandRunner(object):
    "Run commands with the 'subprocess' module"
    def __init__(self):
        try:
            from subprocess import Popen, PIPE
        except ImportError:
            # Python 2.2 and 2.3 compatibility
            from compatibility.subprocess import Popen, PIPE
        self._Popen = Popen
        self._PIPE = PIPE

    def run(self, args, input=None):
        p = self._Popen(args, stdin=self._PIPE, stdout=self._PIPE, stderr=self._PIPE)
        stdout, stderr = p.communicate(input)
        return stdout, stderr, p.returncode

class IronPythonCommandRunner(object):
    "Run commands with .NET's API (IronPython currently lacks 'subprocess')"
    def __init__(self):
        from System.Diagnostics import Process
        self._Process = Process

    def run(self, args, input=None):
        have_stdin = input is not None
        p = self._Process()
        p.StartInfo.UseShellExecute = False
        p.StartInfo.RedirectStandardInput = have_stdin
        p.StartInfo.RedirectStandardOutput = True
        p.StartInfo.RedirectStandardError = True
        p.StartInfo.FileName = args[0]
        p.StartInfo.Arguments = " ".join(args[1:])
        p.Start()
        if have_stdinA:
            p.StandardInput.Write(input)
        p.WaitForExit() 
        stdout = p.StandardOutput.ReadToEnd()
        stderr = p.StandardError.ReadToEnd()
        return stdout, stderr, p.ExitCode

def _choose_run_command():
    errors = []
    try:
        return SubprocessCommandRunner().run
    except ImportError, e:
        errors.append(e)

    try:
        return IronPythonCommandRunner().run
    except ImportError, e:
        errors.append(e)

    raise RuntimeError("couldn't find a working command runner", errors)

_run_command_impl = None
def run_command(args, input=None):
    """run_command(args, input=None) -> stdoutstring, stderrstring, returncode
    Runs the command, giving the input if any.
    The command is specified as a list: 'ls -l' would be sent as ['ls', '-l'].
    Returns the standard output and error as strings, and the return code"""
    global _run_command_impl
    if _run_command_impl is None:
        _run_command_impl = _choose_run_command()
    return _run_command_impl(args, input)

