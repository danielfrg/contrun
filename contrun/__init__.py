import os
import pkgutil
import functools
from tornado import ioloop
import click

modify_times = {}
watched_files = []
process = None


def get_all_sources(path, ret=None):
    """
    Recursively get all the source (*.py) files from the project
    """
    ret = [] if ret is None else ret
    for importer, module_name, ispkg in pkgutil.walk_packages([path]):
        if ispkg:
            new_path = os.path.join(path, module_name)
            get_all_sources(new_path, ret=ret)
        else:
            filename = "{}.py".format(os.path.join(path, module_name))
            if os.path.exists(filename):
                ret.append(filename)
            else:
                print("Source not found: {}".format(filename), err=True)


def reload_on_update(modify_times):
    for path in watched_files:
        try:
            modified = os.stat(path).st_mtime
        except Exception:
            return
        if path not in modify_times:
            modify_times[path] = modified
            return
        if modify_times[path] != modified:
            modify_times[path] = modified
            print("{} modified".format(path))
            reload_()


# def reload_():
#     print("Reloading modules and restarting server")
#     server.stop(0)
#     reload_package()
#     create_new_server()
#     server.start()


# watched_files = []
# get_all_sources(".", watched_files)
#
# modify_times = {}
# for path in watched_files:
#     modify_times[path] = os.stat(path).st_mtime
# callback = functools.partial(reload_on_update, modify_times)
#
# io_loop = ioloop.IOLoop()
# scheduler = ioloop.PeriodicCallback(callback, 500, io_loop=io_loop)
# scheduler.start()

# create_new_server()
# server.start()
# io_loop.start()
#
#
# def main():
#     cmd = " ".join(sys.argv[1:])
#     if cmd:
#         do_command_on_update(cmd)
#     else:
#         print("Usage: %s command args ..." % __file__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
@click.argument("command")
@click.argument("directory", type=click.Path(exists=True), default=".")
def cli(ctx, command, directory):
    print(ctx.invoked_subcommand)
    if ctx.invoked_subcommand is None:
        return ctx.invoke(contrun_cmd, ctx.obj, command, directory)


# @cli.command("run")
# @click.pass_context
# @click.argument("command")
# @click.argument("directory", type=click.Path(exists=True), default=".", required=False)
# def contrun_cmd(ctx, command, directory):
#     print(":)")


def main():
    cli(obj={})

if __name__ == "__main__":
    main()

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
