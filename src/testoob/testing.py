def _run_command_subprocess(cmd, input):
    import subprocess
    raise NotImplementedError

def _run_command_popen2(cmd, input):
    import popen2
    child = popen2.Popen3(cmd, capturestderr=True)

    if input is not None:
        child.tochild.write(input)

    rc = child.wait()

    return child.fromchild.read(), child.childerr.read(), rc

def _run_command(cmd, input=None):
    """_run_command(cmd, input=None) -> stdoutstring, stderrstring, returncode
    Runs the command, giving the input if any.
    Returns the standard output and error as strings, and the return code"""
    try:                return _run_command_subprocess(cmd, input)
    except ImportError: return _run_command_popen2(cmd, input)

def command_line(
        cmd,
        input=None,
        expected_output=None,
        expected_error=None,
        expected_output_regex=None,
        expected_error_regex=None,):
    raise NotImplementedError
