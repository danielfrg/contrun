#!/usr/bin/python
import os
import glob
import functools

from tornado import ioloop
from tornado.process import Subprocess
from tornado.iostream import PipeIOStream

command = ""
process = None

watched_files = []
modify_times = {}


def main(cmd, path, exclude=None, check_time=500):
    global command, watched_files, modify_times
    command = cmd

    watched_files = get_files(path, exclude=exclude)

    io_loop = ioloop.IOLoop.current()

    callback = functools.partial(reload_on_update_, modify_times)
    scheduler = ioloop.PeriodicCallback(callback, check_time, io_loop=io_loop)
    scheduler.start()

    start_process()

    io_loop.start()


def start_process():
    """
    Start a new process.

    If process is running terminate it and start a new one
    """
    global command, process

    def on_data(data):
        data = data.decode().strip()
        print('{}'.format(data))

    cmd = command.split(' ')

    if process:
        process.terminate()

    process = MySubprocess(cmd, -1, functools.partial(on_data), None, None)


class MySubprocess(Subprocess):
    """
    Extends tornado.Subprocess to grab the stdout

    Taken and modified from from http://alexapps.net/python-tornado-subprocess-timeout-and-re/
    """
    def __init__(self, command, timeout=-1, stdout_chunk_callback=None, stderr_chunk_callback=None,
                exit_process_callback=None, stdin_bytes=None,
                io_loop=None, kill_on_timeout=False):
        """
        Initializes the subprocess with callbacks and timeout.

        :param command: command like ['java', '-jar', 'test.jar']
        :param timeout: timeout for subprocess to complete, if negative or zero then no timeout
        :param stdout_chunk_callback: callback(bytes_data_chuck_from_stdout)
        :param stderr_chunk_callback: callback(bytes_data_chuck_from_stderr)
        :param exit_process_callback: callback(exit_code, was_expired_by_timeout)
        :param stdin_bytes: bytes data to send to stdin
        :param io_loop: tornado io loop on None for current
        :param kill_on_timeout: kill(-9) or terminate(-15)?
        """
        self.exit_process_callback = exit_process_callback
        self.kill_on_timeout = kill_on_timeout
        stdin = Subprocess.STREAM if stdin_bytes else None
        stdout = Subprocess.STREAM if stdout_chunk_callback else None
        stderr = Subprocess.STREAM if stderr_chunk_callback else None

        Subprocess.__init__(self, command, stdin=stdin, stdout=stdout, stderr=stderr, io_loop=io_loop)

        self.process_expired = False
        self.terminate_timeout = self.io_loop.call_later(timeout, self.timeout_callback) if timeout > 0 else None

        self.set_exit_callback(self.exit_callback)

        if stdin:
            self.stdin.write(stdin_bytes)
            self.stdin.close()

        if stdout:
            output_stream = PipeIOStream(self.stdout.fileno())

            def on_stdout_chunk(data):
                stdout_chunk_callback(data)
                if not output_stream.closed():
                    output_stream.read_bytes(102400, on_stdout_chunk, None, True)

            output_stream.read_bytes(102400, on_stdout_chunk, None, True)

        if stderr:
            stderr_stream = PipeIOStream(self.stderr.fileno())

            def on_stderr_chunk(data):
                stdout_chunk_callback(data)
                if not stderr_stream.closed():
                    stderr_stream.read_bytes(102400, on_stderr_chunk, None, True)

            stderr_stream.read_bytes(102400, on_stderr_chunk, None, True)

    def timeout_callback(self):
        if self.kill_on_timeout:
            self.proc.kill()
        else:
            self.proc.terminate()
        self.process_expired = True

    def terminate(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.process_expired = True

    def exit_callback(self, status):
        if self.terminate_timeout:
            self.io_loop.remove_timeout(self.terminate_timeout)
        # need to post this call to make sure it is processed AFTER all outputs
        if self.exit_process_callback:
            self.io_loop.add_callback(self.exit_process_callback, status, self.process_expired)


def reload_on_update_(modify_times):
    global process, watched_files
    for path in watched_files:
        check_file(modify_times, path)


def check_file(modify_times, path):
    """
    Check if a file has changed since last time.
    Call `start_process` if it has
    """
    try:
        modified = os.stat(path).st_mtime
    except Exception:
        return
    if path not in modify_times:
        modify_times[path] = modified
    if modify_times[path] != modified:
        print('{} modified; restarting server'.format(path))
        modify_times[path] = modified
        start_process()


def get_files(path, exclude=None):
    """
    Get all files directory (recursively)
    Optionaly exclude one file type
    """
    exclude = exclude or '*.pyc'
    exclude_expr = '{}/**/{}'.format(path, exclude)
    exclude = set(glob.iglob(exclude_expr, recursive=True))

    expr = '{}/**'.format(path)
    paths = set(glob.iglob(expr, recursive=True)) - exclude

    files = []
    for filename in paths:
        if os.path.isfile(filename):
            files.append(os.path.abspath(filename))
    return files
