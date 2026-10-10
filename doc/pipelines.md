<!--
-*- markdown -*-
-*- coding: utf-8 -*-

michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# visualization pipelines: what each channel computes

> **Status, 2026-10-06.** A survey of every channel the readers offer, written while drawing the
> pipeline of a view in the visualization pipeline activity. It records what each channel
> computes, stage by stage, which of those stages pyre's visualization factories can describe,
> which ones are specific to qed, and which channels have a flow that describes them so far. The
> pipelines that are not described yet push on the visual language of the diagram in different
> ways; they are to be designed one at a time, with the gaps below as the starting list.

## how a channel is drawn

A reader's channel class names the flow that describes it through the class method
`description()`; the base channel of each reader family answers `None`, and the view then says
that there is no description of the pipeline of the channel yet. The flows live in
`pkg/channels`, as `pyre.flow` workflows built out of the factories of `pyre.viz`; the base
`qed.channels.channel` contributes the `bmp` encoder and the image it makes. The view draws the
flow of its channel once per channel, read only, since a change to the diagram does not reach the
pipeline that renders the tiles.

A flow describes the stages after the data is read. Its leftmost input slot stands for the tile
of the dataset at the current zoom; the read and the decimation are not drawn. The reasons are in
the section on decimation below.

## what each channel computes

The c++ compositions live in `lib/qed/native/channels`, `lib/qed/nisar`, and `lib/qed/isce2`; the
bindings that build them are in `ext/qed`. Every pipeline ends with the `bmp` encoder.

### native readers: flat, ENVI, CEOS, GDAL

Family `qed.channels.native.*`, in `pkg/readers/native/channels`. Datasets offer channels by cell
type: complex cells get `complex`, `amplitude`, `phase`, `real`, and `imaginary`; real and integer
cells get `value` and `abs`; GDAL bands get only `value`. `Channel.tile` calls
`qed.libqed.native.channels.<tag>` with a stride of `2**zoom` per axis.

| tag | controllers | pipeline |
|---|---|---|
| `amplitude` | `amplitude`: log range | decimate → amplitude → parametric(10^low, 10^high) → gray |
| `real`, `imaginary` | `range`: linear range | decimate → real or imaginary → parametric → gray |
| `value` | `range`: linear range | decimate → parametric → gray |
| `abs` | `range`: linear range | decimate → amplitude → parametric → gray |
| `phase` | `phase`: linear range; `brightness`, `saturation`: values | decimate → cycle(low, high) → affine(0, 2π) → hsb hue; constants for saturation and brightness |
| `complex` | `amplitude`: log range; `phase`: linear range; `saturation`: value | decimate → cycle → affine(0, 2π) → hsb hue; decimate → amplitude → parametric → hsb brightness; a constant saturation |

Notes:
- `abs` names the amplitude selector only in its type: `lib/qed/native/channels/magnitude.icc`
  passes the decimator, and the selector is built implicitly; for a real cell it computes the
  magnitude.
- In `complex` and `phase`, `cycle` maps the phase as a fraction of a turn onto the interval of
  the controller, and `affine` clips it to [0,1]: the controller rescales the hue rather than
  selecting a window of phases.
- A tile of a foreign byte order, or one that is not aligned, is decimated while it is copied, by
  `qed::py::copyTile` (`ext/qed/grid.icc`); the kernel then runs with a stride of one.
- GDAL decimates in python, by slicing (`pkg/readers/native/datasets/GDALBand.py`), and renders
  parametric → gray over the slice.

### NISAR products

Family `qed.channels.nisar.*`, in `pkg/readers/nisar/products/channels`. `Channel.tile` resolves
`qed.libqed.nisar.<category>.<tag>`, and `Product.resolve` picks the pyramid level and the stride
that remains, with the mask at the same depth. The read is the decimation: a strided hyperslab of
the dataset, or a level of the pyramid (`lib/qed/nisar/fetch.icc`). Channels with `absence` set
also receive the fill value of the dataset.

| tag | used by | pipeline |
|---|---|---|
| `complex`, `amplitude`, `phase`, `real`, `imaginary` | RSLC, GSLC, the complex layers of GUNW, RIFG, GCOV | fetch, then the native pipeline with a stride of one |
| the BFPQ variants of the five | RRSD | strided read of encoded IQ → **BFPQ decode** → the native pipeline |
| `value` | real, mask, and offset layers | fetch → parametric → gray |
| `abs` | same | fetch → amplitude → parametric → gray |
| `coherence` | GUNW, RIFG, RUNW | fetch → parametric → gray → **Absence** |
| `covariance` | GCOV | fetch → parametric(10^low, 10^high) → gray → **Absence** |
| `coherenceMasked` | GUNW, RIFG, RUNW | fetch data and mask → parametric → gray → **MaskedCoherence** → **Absence** |
| `covarianceMasked` | GCOV | fetch data and mask → parametric → gray → **MaskedCovariance** → **Absence** |
| `unwrapped` | GUNW, RUNW | fetch → parametric(low, high) → affine(0, 2π) → hl hue; a constant luminosity → **Absence** |
| `unwrappedMasked` | GUNW, RUNW | as `unwrapped`, with **MaskedPhase** before **Absence** |
| `gunw` | the GUNW mask | fetch → **GUNWMask palette** |
| `gcov` | the GCOV mask | fetch → **GCOVMask palette** |

Notes:
- `unwrapped` clips through `parametric`, so the hue saturates outside the interval of the
  controller; it does not wrap.
- `hl` uses its default threshold, 0.4, in c++ and in its python description.

### stacks

`pkg/stacks/Dataset.py` registers two channels from the NISAR package. Both read every member
with a stride of `2**zoom`, ignoring the pyramid (`ext/qed/nisar/stack.cc`).

| tag | controllers | pipeline |
|---|---|---|
| `meanpower` | `power`: log range | per member read → **MeanPower** mean of \|z\|² → parametric → gray |
| `coherence` | `range`: linear range, pinned to [0,1] | per member read → **Coherence** \|Σz\| / Σ\|z\| → parametric → gray |

The stack channels have no quantity, so their controllers are not coupled to other channels.

### isce2

All isce2 channels decimate in c++.

Interferograms (`pkg/readers/isce2/interferogram/channels`), complex cells:

| tag | pipeline |
|---|---|
| `amplitude` | decimate → amplitude → parametric → gray |
| `real`, `imaginary` | decimate → real or imaginary → parametric → gray |
| `phase` | decimate → cycle → affine(0, 2π) → **hl** hue; a constant luminosity |
| `complex` | decimate → cycle → affine → **hl** hue; decimate → amplitude → parametric → **hl** luminosity; no saturation controller |

Unwrapped interferograms (`pkg/readers/isce2/unwrapped/channels`) are line interleaved: band 0
holds the amplitude, band 1 the unwrapped phase. The band is chosen by the origin and the shape
of the decimation of a rank 3 grid.

| tag | controllers | pipeline |
|---|---|---|
| `amplitude` | `scale`, `exponent`: values; `mean` from the statistics, not a trait | decimate band 0 → power(mean, scale, exponent) → gray |
| `phase` | `phase`: linear range; `brightness`: value | decimate band 1 → parametric → affine(0, 2π) → hl hue; a constant luminosity |
| `complex` | `scale`, `exponent`, `phase` | band 0 → power → hl luminosity; band 1 → parametric → affine → hl hue |

### controllers

- `linearRange`: `low` and `high`, unset by default, bounded by ±1e3.
- `logRange`: `low` -6, `high` 3, bounded by -7 and 4; the values are exponents, and the channel
  passes `10**low` and `10**high` to the pipeline. The conversion is in the python channel, not a
  stage of the pipeline.
- `value`: 0.5, in [0,1].
- A controller with a `quantity` is shared by every channel of a dataset that names the same
  quantity (`pkg/controllers/couple.py`): the amplitude of `amplitude` and `complex`, the phase of
  `phase` and `complex`.

## the stages that are specific to qed

None of these is a factory of `pyre.viz`; they belong in qed.

- **fetch** (`lib/qed/nisar/fetch.icc`): the strided read of a NISAR dataset, or of a level of its
  pyramid, which yields fill where nothing was written. With `Product.resolve`, it is the source
  and the decimation of every NISAR channel.
- **BFPQ decode** (`lib/qed/nisar/bfpq/*.icc`): a lookup per cell that turns encoded IQ pairs into
  complex values.
- **Absence** (`lib/qed/nisar/Absence.icc`): the outermost gate, after the colormap and any mask
  gate. It reads the raw cell and the color, and paints a cell that holds the fill value as
  "declared" (0.10, 0.05, 0.05), a NaN cell when the fill is not NaN as "undeclared" (0.04, 0.11,
  0.10), and passes every other color through.
- **MaskedCoherence**, **MaskedPhase** (`lib/qed/nisar/MaskedCoherence.icc`, `MaskedPhase.icc`):
  read the mask, reduce `mask & 0xff` modulo 100, and paint the cell black when either decimal
  digit is zero; every other color passes.
- **MaskedCovariance** (`lib/qed/nisar/MaskedCovariance.icc`): mask 255 paints (0.10, 0.05, 0.05),
  mask 0 paints black, every other color passes.
- **GUNWMask palette** (`lib/qed/nisar/GUNWMask.icc`): a lookup on `code & 0xff`: 255 is a dark
  red; land codes 10·reference + secondary get an oklch hue per reference subswath, darker for
  later secondary subswaths; 100 is a pale blue; water codes 100 + land code blend their hue
  toward blue; everything else is black. It replaces the colormap.
- **GCOVMask palette** (`lib/qed/nisar/GCOVMask.icc`): codes 1 through 5 take the colors of the
  GUNW diagonal, 255 is a faint red, everything else is black.
- **MeanPower**, **Coherence** reducers (`lib/qed/native/channels/MeanPower.icc`,
  `Coherence.icc`): many inputs, one output.
- **The band slice** of isce2 unwrapped interferograms, carried by the origin and the shape of a
  rank 3 decimation.
- **The tile copy** of the native readers (`onTile`, `copyTile`), which swaps or aligns the bytes
  while it decimates.

## what is described so far

| flow | factories | describes |
|---|---|---|
| `qed.channels.value` | parametric → gray → bmp | native `value`; NISAR `value`, `coherence`, `coherenceMasked` |
| `qed.channels.amplitude` | amplitude → parametric → gray → bmp | `amplitude` and `abs` of the native and NISAR readers, BFPQ `amplitude`, isce2 interferogram `amplitude` |
| `qed.channels.real`, `qed.channels.imaginary` | real or imaginary → parametric → gray → bmp | the same readers' `real` and `imaginary` |
| `qed.channels.covariance` | parametric → gray → bmp | NISAR `covariance`, `covarianceMasked` |
| `qed.channels.phase` | hsb → bmp | native and NISAR `phase`, BFPQ `phase` |

Every other channel has no description, and its pipeline pane says so: `complex` everywhere, isce2
interferogram `phase`, every isce2 unwrapped channel, NISAR `unwrapped` and `unwrappedMasked`, the
two masks, and the two stack channels.

`qed.channels.covariance` and `qed.channels.value` are the same flow; one of them should go when
the descriptions settle.

## the gaps

Each of these is a place where a drawn pipeline is incomplete or where the visual language has no
answer yet. They are to be taken one at a time.

1. **The source and the decimation are not drawn.** The NISAR read is the decimation; the native
   readers decimate with a stride per axis, which the `decimate` description, with its single
   `level`, cannot express; isce2 unwrapped slices a band in the same step. The input slot of a
   flow stands for all of this. Datasets as products of the diagram are the likely answer: the
   input slot would be bound to the dataset, at the zoom of the view.
2. **`qed.channels.phase` is wired incompletely.** Its `hsb` inputs are unbound: the cycle, the
   affine map, and the two constants are missing. The diagram of a phase channel shows only the
   colormap and the encoder.
3. **Fan out.** `complex` and the isce2 `phase` and `complex` channels read the same tile along
   two branches that meet at the colormap. The layout engine puts factories in one row today.
4. **Constants.** Saturation and brightness are constant inputs of a colormap, set by a
   controller. A `constant` factory with no input is one way to draw them; a setting of the
   colormap is another.
5. **Gates.** Absence and the three mask gates read the raw signal and a color, and hand back a
   color. They need a factory kind of their own: inputs for the signal and the three channels,
   outputs for the three channels. The masked channels also read a second dataset, the mask, at
   the same origin and stride.
6. **Palettes.** The two mask palettes turn a code into a color. They can implement the colormap
   protocol, but they replace the normalizer and the colormap together.
7. **Reducers.** The stack reducers take any number of inputs, one per member; the slots of a
   factory are fixed. One input that stands for the stack is a possibility.
8. **BFPQ decode.** A filter between the read and the rest of the pipeline; drawn with gap 1.
9. **Controllers.** The diagram shows the settings of a fresh flow, not the values the controllers
   of the view hold, and a log range is converted in python before it reaches `parametric`. Both
   are needed for the inspector to describe the pipeline that renders the tiles.

## the visual language: kinds and levels

> **Speculative, 2026-10-06.** A line of thought recorded so that it is not lost, not a design.
> Nothing in this section is decided or implemented; it is a set of candidates and questions to
> weigh before the language is settled. Read it as such.

### the idea

pyre has three levels for anything configurable: a protocol, the component classes that
implement it, and the instances of those classes. The thought is that the three levels apply to
the data of a pipeline, its products, as well as they apply to its processing engines, its
factories, and that all six combinations are useful in a diagram:

- A flow drawn only with protocols would be a high level description of the shape of a pipeline.
- Putting a component class in place of a protocol would be an instruction to whoever orchestrates
  the execution: use this kind of implementer here.
- Before anything runs, every abstract node would have to be replaced by a concrete instance.

This lines up with how a pyre facility is bound today: a trait typed by a protocol, with a
`pyre_default` that names a class, and an instance once the component is built. The descriptions
in `pkg/channels` already mix the levels: `normalizer = qed.viz.filter()` is typed by a protocol,
its default names the class `parametric`, and building the flow makes the instance.

### a possible encoding

If every entity is drawn as a puck, the kind and the level have to be told apart by paint. One
candidate: the hue says the kind, as it does today, and the fill says the level.

| | protocol | component class | instance |
|---|---|---|---|
| factory | orange outline, hollow | orange outline, tinted | solid orange |
| product | blue outline, hollow | blue outline, tinted | solid blue |

In this reading, today's gray slot is a product protocol, a specification in `pyre.flow`, and
would become a hollow blue puck. The diagrams have no factory protocols yet, the producers of
`pyre.flow`.

Dark fills on a dark canvas are close in value, and fill alone is a weak cue for some viewers, so
a second cue may be needed: perhaps a dashed outline for protocols and a solid one for classes
and instances, in the flat icons and the isometric pucks alike.

### realizing a pipeline

A diagram drawn this way would also show how far a pipeline is from running: anything hollow or
tinted is still to be resolved. Realizing it would mean walking the diagram, replacing every
protocol by its default or chosen implementer and every class by an instance. Whether this is a
step the user takes, the orchestrator takes, or both, is open.

### open questions

1. **Containers.** No factory has a slot that holds a container of products yet. The stack
   reducers need one: their inputs grow with the stack. Whether a container is a product of its
   own, a slot that admits many bindings, or an arity fixed at realization, is to be ironed out.
   The pyre 2.0 proposal (`doc/design/lifecycle.md` on pyre's branch `p2`, 6.4.3) treats list,
   set, and dictionary traits whose schema is a protocol as facilities, which the flow engine
   cannot see today.
2. **Settings.** Traits that are neither inputs nor outputs, e.g. the interval of `parametric`,
   are settings. A change to a setting must dirty its factory, so that the consumers downstream
   know their products are stale. Whether `pyre.flow` does this fully is not known. The pyre 2.0
   proposal derives staleness from a revision number per instance that increases when any of its
   traits, or any of its parts, changes (6.6.1).
3. **Completeness of `pyre.flow`.** Before `pyre.flow` is taken apart and rebuilt around the
   component lifecycle (the pyre 2.0 proposal, 8.1), it is worth auditing how much of the above it
   already captures: the levels, the realization, containers, and the dirtying by settings.
4. **Prior art.** pyre has a draft of a visual language for workflows from 2017, in
   `doc/diagrams/packages/pyre.flow.graffle`, worth consulting before settling anything here.
5. **Expressiveness.** The test of the language is whether every pipeline can be drawn with it:
   the channels in this survey, with their gates, palettes, reducers, constants, and branches that
   split and rejoin, and the pipelines users will design.

## defects found during the survey

Recorded on the pile, not fixed here.

- BFPQ `real` and `imaginary` hand the encoded tile to the native kernel instead of the decoded
  one (`lib/qed/nisar/bfpq/real.icc`, `imaginary.icc`); they render undecoded data. Parked, with
  the change of the IQ cell type.
- `Magnitude.gdal` (`pkg/readers/native/channels/Magnitude.py`) calls an overload of
  `qed.libqed.native.channels.abs` that has no binding; nothing calls it today.
- pyre's `lib/pyre/viz/iterators/filters/Real.icc` says "compute the magnitude" over `std::real`.
- Open question: the MaskedCoherence and MaskedPhase gates reduce the mask modulo 100, which turns
  the fill code 255 into 55 and lets water codes other than 100 through. Absence catches the fill
  in practice.


<!-- end of file -->
