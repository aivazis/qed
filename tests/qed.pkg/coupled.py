#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the channels of a dataset share the controllers of the quantities they have in
common: the complex channel and the amplitude channel share one amplitude controller, the
complex and phase channels share the phase and the saturation, both in the reference channels
of the dataset, which draw their configuration from {dataset}.controllers, and in the pipelines
of a view, where an edit through one channel shows through the other
"""

# externals
import struct

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# get the reader
reader, *_ = ux.store.sources
# and its dataset
dataset, *_ = reader.datasets
# its reference channels
channels = dataset.channels

# the complex and amplitude channels share one amplitude controller
amplitude = channels["complex"].amplitude
assert channels["amplitude"].amplitude is amplitude
# which the dataset owns, under the name of the quantity
assert amplitude.pyre_name == "d16.data.controllers.amplitude"
# and which draws its configuration from there
assert amplitude.auto is False
assert (amplitude.min, amplitude.low, amplitude.high, amplitude.max) == (-1.0, -0.5, 0.5, 1.0)
# the complex and phase channels share the phase
assert channels["phase"].phase is channels["complex"].phase
assert channels["phase"].phase.pyre_name == "d16.data.controllers.phase"
# and the saturation
assert channels["phase"].saturation is channels["complex"].saturation
assert channels["phase"].saturation.pyre_name == "d16.data.controllers.saturation"
# while the real and imaginary parts keep ranges of their own
assert channels["real"].range is not channels["imaginary"].range
assert channels["real"].range.pyre_name == "d16.data.real.range"

# get the view in the only viewport
view = ux.store._viewports[0].view()
# its complex and amplitude pipelines
complex = view.pipeline(channel="d16.data.complex")
magnitude = view.pipeline(channel="d16.data.amplitude")
# share an amplitude controller of their own, apart from the reference one
shared = complex.amplitude
assert magnitude.amplitude is shared
assert shared is not amplitude
# named after the quantity under the namespace of the dataset in the view
assert shared.pyre_name == f"{view.pyre_name}.d16.data.controllers.amplitude"
# which mirrors the reference
assert (shared.min, shared.low, shared.high, shared.max) == (-1.0, -0.5, 0.5, 1.0)

# move the picks of the amplitude through the complex channel
ux.store.vizUpdateController(
    viewport=0,
    channel=complex.pyre_name,
    name="amplitude",
    configuration={"min": -2.0, "low": -0.75, "high": 0.75, "max": 2.0},
)
# the amplitude channel shows the same picks
assert (magnitude.amplitude.low, magnitude.amplitude.high) == (-0.75, 0.75)
# and the same extent
assert (magnitude.amplitude.min, magnitude.amplitude.max) == (-2.0, 2.0)
# while the reference is untouched
assert (amplitude.min, amplitude.low, amplitude.high, amplitude.max) == (-1.0, -0.5, 0.5, 1.0)

# reset it through the amplitude channel
ux.store.vizResetController(viewport=0, channel=magnitude.pyre_name, name="amplitude")
# and the complex channel is back at the reference too
assert (complex.amplitude.min, complex.amplitude.low) == (-1.0, -0.5)
assert (complex.amplitude.high, complex.amplitude.max) == (0.5, 1.0)

# a small wrapped interferogram, a raster of complex cells
with open("coupled.int", "wb") as product:
    # all of them one
    product.write(struct.pack(f"{2 * 8 * 8}f", *([1.0, 0.0] * 8 * 8)))
# open it
interferogram = qed.readers.isce2.int(name="coupled.int", uri="coupled.int", shape=(8, 8))
interferogram.open(measure=False)
# get its dataset
(wrapped,) = interferogram.datasets
# its complex and phase channels share the phase
phase = wrapped.channel(name="complex").phase
assert wrapped.channel(name="phase").phase is phase
# which spans one cycle of the colors
assert (phase.min, phase.low, phase.high, phase.max) == (0, 0, 1, 1)

# the NISAR fixture; part of the shared test data tree
product = qed.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
# if it has been generated
if product.exists():
    # open the product
    gcov = qed.readers.nisar.gcov(name="coupled", uri=f"file:{product}")
    gcov.open(measure=False)
    # pick a covariance term
    term = next(dataset for dataset in gcov.datasets if dataset.pyre_name.endswith("L.A.HHHH"))
    # its plain and masked channels share the amplitude
    covariance = term.channel(name="covariance").amplitude
    assert term.channel(name="covarianceMasked").amplitude is covariance
    # under the name of the quantity in the namespace of the term
    assert covariance.pyre_name == f"{term.pyre_name}.controllers.amplitude"


# end of file
