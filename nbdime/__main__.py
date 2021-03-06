# coding: utf-8

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import unicode_literals
from __future__ import print_function

import sys
from subprocess import call

import nbdime
from ._version import __version__

try:
    from shutil import which
except ImportError:
    from backports.shutil_which import which

COMMANDS = ["show", "diff", "merge", "diff-web", "merge-web", "mergetool",
            "config-git", "reg-extensions"]
HELP_MESSAGE_VERBOSE = ("Usage: nbdime [OPTIONS]\n\n"
                       "OPTIONS: -h, --version, COMMANDS{%s}\n\n"
                       "Examples: nbdime --version\n"
                       "          nbdime show -h\n"
                       "          nbdime merge-web\n\n"
                       "          nbdime config-git (--enable | --disable)"
                       "Documentation: https://nbdime.readthedocs.io" % ", ".join(COMMANDS))


def main_mergetool(args):
    if not which('git'):
        sys.exit("Cannot use \"nbdime mergetool\" alias as git is not preset on path")
    to_call = 'git mergetool --tool=nbdime'.split()

    if args:
        paths = [a for a in args if a.endswith(".ipynb")]
        if len(paths) != len(args):
            nbdime.log.warning("Skipping given filenames without .ipynb extension: {}".format([a for a in args if a not in paths]))
    else:
        paths = ["*.ipynb"]
    to_call.extend(paths)

    nbdime.log.info("Calling 'git mergetool --tool=nbdime' on files {}".format(paths))

    return call(to_call)


def main_dispatch(args=None):
    if args is None:
        args = sys.argv[1:]
    if len(args) < 1:
        sys.exit("Option missing.\n\n%s" % HELP_MESSAGE_VERBOSE)

    cmd = args[0]
    args = args[1:]

    if cmd == "show":
        from nbdime.nbshowapp import main
    elif cmd == "diff":
        from nbdime.nbdiffapp import main
    elif cmd == "merge":
        from nbdime.nbmergeapp import main
    elif cmd == "diff-web":
        from nbdime.webapp.nbdiffweb import main
    elif cmd == "merge-web":
        from nbdime.webapp.nbmergeweb import main
    elif cmd == 'mergetool':
        main = main_mergetool
    elif cmd == 'server':
        from nbdime.webapp.nbdimeserver import main
    elif cmd == 'config-git':
        # Call all git configs
        from nbdime.vcs.git.diffdriver import main as diff_driver
        from nbdime.vcs.git.difftool import main as diff_tool
        from nbdime.vcs.git.mergedriver import main as merge_driver
        from nbdime.vcs.git.mergetool import main as merge_tool
        args = ['config'] + args
        # Short-circuit on first non-zero return code:
        return (
            diff_driver(args) or
            merge_driver(args) or
            diff_tool(args) or
            merge_tool(args)
        )
    elif cmd == 'reg-extensions':
        # Register nbdime extensions
        call('jupyter serverextension enable --py nbdime'.split() + args)
        call('jupyter nbextension install --py nbdime'.split() + args)
        call('jupyter nbextension enable --py nbdime'.split() + args)
        return 0
    else:
        if cmd == '--version':
            sys.exit(__version__)
        if cmd == '-h' or cmd == '--help':
            sys.exit(HELP_MESSAGE_VERBOSE)
        if cmd == '--config':
            # List all possible config options:
            from .config import get_defaults_for_argparse, entrypoint_configurables
            from .prettyprint import pretty_print_dict, PrettyPrintConfig
            print('All available config options, and their current values:\n',
                  file=sys.stderr)
            for entrypoint, cls in entrypoint_configurables.items():
                pretty_print_dict({
                        cls.__name__: get_defaults_for_argparse(entrypoint),
                    },
                    config=PrettyPrintConfig(out=sys.stderr)
                )
                print('', file=sys.stderr)
            sys.exit(1)
        else:
            sys.exit("Unrecognized command '%s'\n\n%s." %
                     (cmd, HELP_MESSAGE_VERBOSE))
    return main(args)


if __name__ == "__main__":
    # This is triggered by "python -m nbdime <args>"
    sys.exit(main_dispatch())
