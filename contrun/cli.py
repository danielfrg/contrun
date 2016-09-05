import click

import contrun
from contrun import core


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(prog_name="Anaconda Deploy", version=contrun.__version__)
@click.pass_context
@click.argument("command")
@click.argument("directory", type=click.Path(exists=True), default=".")
def cli(ctx, command, directory):
    core.main(command, directory)


def main():
    cli(obj={})
