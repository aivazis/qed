# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal


# the report a survey ships back to the team
class Discovery:
    """
    The discovery record of a data product: everything the server needs to know about a
    source without ever touching its file

    The record is authored on the worker side, after the crew member's own first contact,
    from the metadata each dataset reports about itself; it is a nest of plain values, so it
    pickles cleanly and carries no file handles. Hydration configures the passive team side
    reader with metadata-only dataset twins, the availability map, and the selections as
    first contact left them, auto-picks included
    """

    # interface - worker side
    @classmethod
    def compose(cls, reader):
        """
        Build the discovery record of {reader}, which has just made first contact
        """
        # initialize the pile of findings
        findings = []
        # go through the datasets the reader discovered
        for dataset in reader.datasets:
            # ask each one to describe itself
            finding = dataset.survey()
            # record where its name sits relative to its owner's, so its twin can be
            # named the same way
            finding.suffix = dataset.pyre_name[len(reader.pyre_name) :]
            # and the selector that identifies it
            finding.selector = dict(dataset.selector)
            # the rasters it is read alongside travel by name, relative to the reader, so
            # their twins can be wired together the way the live datasets are
            finding.companions = {
                role: companion.pyre_name[len(reader.pyre_name) :]
                for role, companion in getattr(dataset, "companions", dict)().items()
            }
            # add it to the pile
            findings.append(finding)
        # the availability map travels as plain sequences
        available = {axis: tuple(values) for axis, values in reader.available.items()}
        # flat flavors deduce their shape from the file, so it travels too
        shape = getattr(reader, "shape", None)
        # the identifier the product carries for itself is read off the open file, so it
        # travels as well: it names whatever is derived from the product, and the passive
        # reader must name it the same way
        granule = getattr(reader, "granule", None)
        # assemble the record
        return cls(
            selections=dict(reader.selections),
            available=available,
            shape=tuple(shape) if shape else None,
            findings=findings,
            granule=granule,
        )

    # interface - team side
    def hydrate(self, reader):
        """
        Configure the passive {reader} from my contents, materializing metadata-only twins
        of the datasets the survey found
        """
        # if the reader has already made contact, e.g. through the blocking path
        if getattr(reader, "_opened", False):
            # leave it alone
            return reader
        # readers that complete their configuration at first contact, e.g. the flat flavors
        # that deduce their shape from the file size, adopt the surveyed value
        if self.shape is not None and hasattr(reader, "shape"):
            # install it
            reader.shape = self.shape
        # go through the findings
        for finding in self.findings:
            # resolve the dataset factory
            factory = qed.protocols.dataset.pyre_resolveSpecification(spec=finding.factory)
            # and materialize a metadata-only twin: it opens no file, and the seed carries
            # what the surveying worker measured, so its channels autotune exactly as they
            # would have on the live path
            dataset = factory(
                # the twin is named the way the live dataset was
                name=f"{reader.pyre_name}{finding.suffix}",
                # it holds no payload
                hydrated=True,
                # the seed statistics stand in for the sample the live path collects
                seed=finding.stats,
                # the layout
                uri=reader.uri,
                cell=finding.cell,
                shape=finding.shape,
                origin=finding.origin,
                tile=finding.tile,
                # and the identity
                selector=finding.selector,
            )
            # add it to the reader's pile
            reader.datasets.append(dataset)
        # the twins by their suffix, so companions can find each other
        twins = {
            finding.suffix: twin
            for finding, twin in zip(self.findings, reader.datasets[-len(self.findings) :])
        }
        # go through the findings again
        for finding in self.findings:
            # and wire each twin to the twins of its companions, under the role each plays
            for role, suffix in finding.companions.items():
                # a companion the survey did not report is a bug in the survey
                if suffix not in twins:
                    # make a channel
                    channel = journal.firewall("qed.nexus.survey")
                    # complain
                    channel.line(f"while hydrating '{reader.pyre_name}{finding.suffix}'")
                    channel.line(
                        f"its '{role}' companion '{reader.pyre_name}{suffix}' was not surveyed"
                    )
                    # flush
                    channel.log()
                    # and move on
                    continue
                # otherwise, wire it
                setattr(twins[finding.suffix], role, twins[suffix])
        # a reader that names its product from the file learns the name from the survey
        if self.granule is not None and hasattr(type(reader), "granule"):
            # so it can name what is derived from the product the way the crew does
            reader.granule = self.granule
        # install the availability map
        reader.available = {axis: set(values) for axis, values in self.available.items()}
        # adopt the selections as the survey left them: the worker rebuilt the reader from
        # its recipe, so they are the user's configuration plus the open-time auto-picks
        reader.selections = dict(self.selections)
        # leave the first-contact mark: the reader's knowledge is now complete, even though
        # this process never touched the file
        reader._opened = True
        # show me
        channel = journal.debug("qed.nexus.survey")
        # what arrived
        channel.log(f"hydrated '{reader.pyre_name}' with {len(self.findings)} datasets")
        # hand the reader back
        return reader

    # metamethods
    def __init__(self, selections, available, shape, findings, granule=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # the identifier the product carries for itself, if any
        self.granule = granule
        # the selections as they stood after first contact, auto-picks included
        self.selections = selections
        # the availability map, as plain sequences so the record pickles cleanly
        self.available = available
        # the resolved reader shape, for the flavors that deduce it from the file
        self.shape = shape
        # the per-dataset findings
        self.findings = findings
        # all done
        return


# end of file
