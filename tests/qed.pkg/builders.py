#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a reader's builders and the team that serves its tiles are separate teams, with the
budgets of their caches, and that a worker opens its reader with the budgets of its team
"""

# support
import journal
import pyre
import qed

# the reader complains about the missing web assets on open; this driver is not the app
journal.warning("qed.cli").deactivate()

# the fleet, with an event loop of its own that is never run here
fleet = qed.nexus.fleet(name="builders.fleet")
fleet.dispatcher = pyre.ipc.newPSL()

# the team that serves the tiles of a reader
tiles = fleet.team(reader="product")
# and its builders
builders = fleet.builders(reader="product")
# are different teams
assert tiles is not builders
# of different kinds
assert tiles.kind == "tile" and builders.kind == "build"
# formed once each
assert fleet.team(reader="product") is tiles and fleet.builders(reader="product") is builders
# the builders stream: a page buffer for the pages of the task in hand, and the library's chunks
assert builders.budget() == {"pages": 16 * 1024}
# the tiles revisit: the reader's page buffer, and a chunk cache that holds a view's chunks
assert tiles.budget() == {"chunks": 256}
# the fleet describes both
assert sorted(team["kind"] for team in fleet.describe()) == ["build", "tile"]

# a team marks the tasks it is handed with its budgets, before anything else happens to them;
# a disbanded team turns the task down right away, which is all this needs
stamper = fleet.builders(reader="stamper")
stamper.disband()
# a stand-in for a task
task = qed.nexus.chore()
# the outcome
outcome = []
# hand it over
stamper.assign(task=task, callback=lambda result, error: outcome.append(error))
# it was marked
assert task.budget == {"pages": 16 * 1024}
# and turned down
assert outcome and outcome[0] is not None

# releasing the builders takes them off the roster
fleet.retire(reader="product")
assert "product" not in fleet.builds
# pyre hands back the same team for the same name, which stood down rather than disbanded, so
# it is ready to recruit again when the next build arrives
again = fleet.builders(reader="product")
assert again is builders and not again._disbanded
# the same goes for the team that serves the tiles of a reader that is disconnected and
# connected again
fleet.dismiss(reader="product")
assert "product" not in fleet.teams
assert fleet.team(reader="product") is tiles and not tiles._disbanded
# letting the fleet go takes everybody
fleet.disband()
assert not fleet.teams and not fleet.builds

# a worker opens its reader with the budgets of its team, for the settings the reader has
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
# a checkout without the fixture has nothing more to check
if not product.exists():
    # so bail quietly
    raise SystemExit(0)
# a reader of a product in hdf5
gcov = qed.readers.nisar.gcov(name="builders.gcov", uri=f"file:{product}")
# described as a survey, the first thing a worker does with a reader
survey = qed.nexus.survey(reader=gcov)
# marked with a budget, and a setting no reader has
survey.budget = {"pages": 16 * 1024, "chunks": 32, "nonsense": 1}
# the worker builds its reader
reader = survey._locateReader(readers={}, measure=False)
# with the budget of its team
assert reader.pages == 16 * 1024 and reader.chunks == 32
# and without the setting it does not have
assert not hasattr(reader, "nonsense")


# end of file
