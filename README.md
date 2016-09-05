# ContRun

Continuously run any command on file changes.

Imagine you are developing a server (e.g. protobuf/grpc) and you don't want to stop and start
the server every 2 seconds while making changes to the code.

## How/why

Similar/inspired by [conttest](https://github.com/eigenhombre/continuous-testing-helper) but can
run process indefinitely. Any `conttest` command has to end before it starts a new one, this
is nice for testing (e.g. `py.test`) but it doesn't work on long running commands
(like servers or even long test suites)

Based on [Tornado autoreload](https://github.com/tornadoweb/tornado/blob/master/tornado/autoreload.py)
but more general (?) - No need to auto reload module or `pkgutil` craziness.

Also tornado autoreload fails and stops the autoreload cycle in some cases: for example any syntax error.
`contrun` subprocess is independent so it will always run and start a new process every file change.

## Installation

```
pip install git+git://github.com/danielfrg/contrun.git
```
