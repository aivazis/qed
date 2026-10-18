#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a refused request comes back as a {NotFound} whose page says why, and that an
installation with no web client answers every request with a page that says what is missing
"""

# externals
import types

# support
import qed
from pyre.http import responses

# a stand-in for the server: it names itself and knows the http responses
server = types.SimpleNamespace(name="qed.test", responses=responses)

# refuse a request, with a reason that carries markup
response = qed.ux.dispatcher._notFound(
    types.SimpleNamespace(), server=server, reason="the tile <0x0> oversteps 'd16'"
)
# it is a {NotFound}
assert response.code == 404
# whose description is the reason, escaped so the page shows it as text
assert response.description == "the tile &lt;0x0&gt; oversteps &#x27;d16&#x27;"
# and the rendered page carries it
assert b"the tile &lt;0x0&gt; oversteps &#x27;d16&#x27;" in response.render()
# while the stock description of the class is untouched
assert responses.NotFound.description == "Nothing matches the given URI"

# a stand-in for an application whose installation has no web client
plexus = types.SimpleNamespace(ux=None, _missing=("qed looked in <here>", "and it is not there"))
# ask it to respond to a request
response = qed.shells.qed.pyre_respond(plexus, server=server, request=None)
# it refuses
assert response.code == 404
# with a page that says the web client is missing, one escaped line per fact
assert response.description == (
    "this installation of qed has no web client:<br>"
    "qed looked in &lt;here&gt;<br>"
    "and it is not there"
)

# a stand-in for the prefix of an installation
prefix = types.SimpleNamespace(uri="/opt/qed")
# and one for an application launched by a script in its {bin} folder
plexus = types.SimpleNamespace(pyre_namespace="qed", pyre_home="/opt/qed/bin")
# when the folder of the web client itself is missing
lines = qed.shells.qed._explainMissingAssets(plexus, prefix=prefix, missing="/opt/qed/etc/qed/ux")
# the explanation says where qed looked, why there, and that the folder is missing
assert lines == (
    "qed serves its web client, the page, script, styles, fonts and images, from",
    "'/opt/qed/etc/qed/ux',",
    "under the installation prefix '/opt/qed',",
    "the parent of '/opt/qed/bin', the folder of the script that launched qed;",
    "but that folder does not exist",
)
# when an ancestor is missing instead, and there was no launching script
plexus.pyre_home = None
lines = qed.shells.qed._explainMissingAssets(plexus, prefix=prefix, missing="/opt/qed/etc")
# the explanation names the ancestor, and credits the package with the prefix
assert lines[2:] == (
    "under the installation prefix '/opt/qed',",
    "where the qed package says it is installed;",
    "but '/opt/qed/etc' does not exist",
)


# end of file
