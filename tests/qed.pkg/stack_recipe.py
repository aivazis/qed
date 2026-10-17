#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that saving a stack records its members and leaves behind what it derives every time it
is built: its uri, its selector table and its aggregate datasets

The selector table is a map, and a map written into a configuration file comes back as text
that pyre evaluates, so a stack that saved it would hand its next boot something it did not
write and may not be able to read
"""

# support
import pyre
import qed

# two members, neither of which ever touches its product
one = qed.readers.nisar.rslc(name="stack_recipe_one", uri="s3://bucket/one.h5")
two = qed.readers.nisar.rslc(name="stack_recipe_two", uri="s3://bucket/two.h5")
# a stack over them
stack = qed.stacks.stack(name="stack_recipe", readers=[one, two])
# which borrowed the selector table of its first member
assert dict(stack.selectors)
# and synthesized its uri
assert str(stack.uri) == "stack:stack_recipe"

# describe it the way the session does when it saves the workspace
recipe = pyre.config.newRecipe().add(stack)
# get the section of the stack
section = recipe.section(name="stack_recipe")
# it names its members
assert "readers" in section
# but none of what it derives
for name in ("uri", "selectors", "datasets"):
    # every time it is built
    assert name not in section, f"the stack saved its {name}"


# end of file
