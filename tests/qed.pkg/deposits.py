#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the plexus resolves its cell, shape, and service settings by depositing
candidates into the configuration store and letting normal arbitration decide

An application registers globally with the journal, so each case runs in its own process
"""

# externals
import subprocess
import sys


# run one scenario in a fresh interpreter and hand back what it prints
def scenario(body: str) -> str:
    """
    Execute {body} in a subprocess and return its output
    """
    # run it
    result = subprocess.run(
        [sys.executable, "-c", body], capture_output=True, text=True, check=True
    )
    # and hand back the trimmed output
    return result.stdout.strip()


# a cell shorthand with a later standing beats an earlier direct assignment
assert (
    scenario(
        "import qed\n"
        "app = qed.shells.qed(name='t', cell='float32', complex64=True)\n"
        "print(app.cell.pyre_family())\n"
    )
    == "qed.datatypes.complex64"
)

# and a direct assignment with a later standing beats an earlier shorthand
assert (
    scenario(
        "import qed\n"
        "app = qed.shells.qed(name='t', complex64=True, cell='float32')\n"
        "print(app.cell.pyre_family())\n"
    )
    == "qed.datatypes.real32"
)

# a lone scalar deposits a partial shape, with a zero in the unspecified rank, for the
# size-based inference of the flat readers to complete
assert (
    scenario("import qed\n" "app = qed.shells.qed(name='t', lines=100)\n" "print(app.shape)\n")
    == "(100, 0)"
)

# a scalar with a later standing merges into an earlier shape
assert (
    scenario(
        "import qed\n"
        "app = qed.shells.qed(name='t', shape=(50, 60), samples=70)\n"
        "print(app.shape)\n"
    )
    == "(50, 70)"
)

# and a shape with a later standing beats an earlier scalar
assert (
    scenario(
        "import qed\n"
        "app = qed.shells.qed(name='t', samples=70, shape=(50, 60))\n"
        "print(app.shape)\n"
    )
    == "(50, 60)"
)

# a web shell serves tiles with the concurrent flavor by default
assert (
    scenario(
        "import qed\n" "app = qed.shells.qed(name='t', shell='web')\n" "print(app.shell.service)\n"
    )
    == "import:qed.nexus.server"
)

# but any real opinion about the service wins over the deposited preference
assert (
    scenario(
        "import pyre, qed\n"
        "pyre.executive.nameserver.insert(\n"
        "    name='t.shell.service', value='http',\n"
        "    priority=pyre.executive.priority.user(),\n"
        "    locator=pyre.tracking.simple('test'))\n"
        "app = qed.shells.qed(name='t', shell='web')\n"
        "print(app.shell.service)\n"
    )
    == "http"
)


# end of file
