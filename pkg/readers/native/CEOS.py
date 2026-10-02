# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import struct
import types

# support
import journal
import qed

# superclass
from .Flat import Flat


# a reader of the image files of CEOS SAR products
class CEOS(Flat, family="qed.readers.native.ceos"):
    """
    A reader of the image file of a CEOS SAR product

    The raster is found from the layout fields of the file descriptor record, the first record of
    the image file, and nothing else: the leader, trailer, and volume files are not consulted.
    Every line of the raster sits in a record of its own, past a prefix whose length the producers
    do not agree on how to report, so the start of the samples is settled by the arithmetic of the
    record length. Layouts that do not follow the rule, such as products whose records vary in
    length, are refused
    """

    # interface
    def _resolveShape(self):
        """
        Complete my cell and shape from the file descriptor record
        """
        # read the layout, and keep it for the dataset construction
        layout = self._layout = self._describe()
        # if it could not be read
        if layout is None:
            # the complaint has been lodged
            return
        # if the user did not pin a cell type
        if not self.cell:
            # the layout supplies it
            self.cell = layout.cell
        # get the current value of my shape
        shape = list(self.shape) if self.shape else [0, 0]
        # fill in whatever the user left out
        if not shape[0]:
            # the height
            shape[0] = layout.lines
        if not shape[1]:
            # the width
            shape[1] = layout.samples
        # set it
        self.shape = tuple(shape)
        # all done
        return

    def _validateSize(self, cell, shape, cellsPerSample):
        """
        Check that the file holds my raster; the layout was checked against the file when it was
        read, so there is nothing left to check beyond its presence
        """
        # a file whose layout could be read holds its raster
        return self._layout is not None

    def _loadDatasets(self, cell, shape):
        """
        Build my datasets: one for each channel of the image file
        """
        # get the layout
        layout = self._layout
        # the number of channels
        channels = layout.channels
        # a file with more than one channel
        if channels > 1:
            # publishes a selector over them, named by their ordinals
            self.selectors = {"band": tuple(str(channel + 1) for channel in range(channels))}
        # go through the channels
        for channel in range(channels):
            # in a band sequential file, each channel is a run of its own lines
            if layout.interleave == "BSQ":
                # so its first line is past all the lines of the channels before it
                first = channel * layout.lines
                # and its lines follow each other
                stride = layout.record
            # in a band interleaved file, the lines of the channels alternate
            else:
                # so its first line is past the first line of each channel before it
                first = channel
                # and its lines are a line of each channel apart
                stride = channels * layout.record
            # build the dataset
            dataset = qed.readers.native.datasets.records(
                # named by the ordinal of its channel
                name=f"{self.pyre_name}.{channel + 1}",
                # the product
                uri=self.uri,
                # the layout of the raster
                shape=shape,
                cell=cell,
                tile=cell.tile,
                # where its first cell sits in the file
                offset=layout.descriptor + first * layout.record + layout.start,
                # and how far apart its lines are
                record=stride,
                # its identity
                selector={"band": str(channel + 1)} if channels > 1 else {},
            )
            # and add it to the pile
            self.datasets.append(dataset)
        # a file with more than one channel
        if channels > 1:
            # has all of them
            self.available = {"band": set(self.selectors["band"])}
        # all done
        return

    # implementation details
    def _describe(self):
        """
        Read the layout of the raster from the file descriptor record
        """
        # the path to the image file
        path = qed.primitives.path(self.uri.address)
        # carefully, since the file may not be there
        try:
            # measure it
            size = path.stat().st_size
            # and open it
            stream = open(path, "rb")
        # if it is not
        except OSError as error:
            # complain
            return self._complain(f"got: {error}")
        # read the records i need, and let go of the file
        with stream:
            # the header of the file descriptor record
            header = stream.read(12)
            # a file too short to hold one
            if len(header) < 12:
                # is not a CEOS image file
                return self._complain("the file is too short to hold a file descriptor record")
            # the sequence number, the record type, and the length of the record
            sequence, kind, descriptor = self._header(header)
            # the file descriptor record of an image file is the first record, and has a type of
            # its own, whatever the producer puts in its first type byte
            if sequence != 1 or kind[1:] != b"\xc0\x12\x12":
                # anything else is not the image file of a CEOS product
                return self._complain("the file does not start with a CEOS file descriptor record")
            # the layout fields end at byte 448 of the record
            if descriptor < 448:
                # so a shorter record cannot hold them
                return self._complain(
                    f"a file descriptor record of {descriptor} bytes is too short"
                )
            # read the rest of it
            record = header + stream.read(descriptor - 12)
            # and the header of the first data record, right after it
            first = stream.read(12)
            # a file without one
            if len(first) < 12:
                # holds no raster
                return self._complain("the file holds no data records")
            # which must be the second record
            sequence, _, length = self._header(first)
            # otherwise the records are not where the descriptor says
            if sequence != 2:
                # so the file is not laid out the way a generic reader expects
                return self._complain(f"the record after the descriptor is record {sequence}")
            # the layout fields
            layout = self._fields(record=record)
            # a record length in the descriptor
            if layout.record is not None and layout.record != length:
                # must agree with the one in the header of the first data record
                return self._complain(
                    f"the descriptor says data records hold {layout.record} bytes",
                    f"but the first one holds {length}",
                )
            # the records i will lay the raster over
            count = layout.records
            # without a count
            if count is None:
                # the file decides
                count = (size - descriptor) // length
            # the file must hold them all
            if size < descriptor + count * length:
                # otherwise the raster runs past its end
                return self._complain(
                    f"{count} records of {length} bytes past a descriptor of {descriptor} bytes",
                    f"require {descriptor + count * length} bytes, but the file holds {size}",
                )
            # go to the header of the last one
            stream.seek(descriptor + (count - 1) * length)
            # read it
            sequence, _, last = self._header(stream.read(12))
            # a last record out of place or of a different length
            if sequence != count + 1 or last != length:
                # means the records vary in length, which a generic reader cannot follow
                return self._complain(
                    f"record {count + 1} is not where records of {length} bytes put it",
                    "the records of this file may vary in length",
                )
        # complete the layout
        return self._settle(layout=layout, descriptor=descriptor, record=length, records=count)

    def _settle(self, layout, descriptor, record, records):
        """
        Derive the placement of the raster in the {records} data records of {record} bytes each
        that follow a descriptor of {descriptor} bytes, from the {layout} fields
        """
        # the bytes of each record in front of the samples, and after them
        prefix = layout.prefix or 0
        suffix = layout.suffix or 0
        # the bytes of each pixel
        group = layout.group
        # without them
        if not group:
            # the cells cannot be told apart
            return self._complain("the descriptor does not say how many bytes each pixel holds")
        # the pixels of each line: the border pixels on either side belong to the line too
        samples = (
            (layout.left or 0) + layout.pixels + (layout.right or 0)
            if layout.pixels is not None
            else None
        )
        # when the descriptor says how many bytes of samples each record holds
        if layout.data is not None:
            # a prefix that already counts the record header adds up to the record length
            if prefix + layout.data + suffix == record:
                # so the samples start right after it
                start = prefix
            # a prefix that does not count it falls short of it by the header
            elif 12 + prefix + layout.data + suffix == record:
                # so the samples start past both
                start = 12 + prefix
            # anything else
            else:
                # does not add up
                return self._complain(
                    f"a prefix of {prefix}, {layout.data} bytes of samples, and a suffix of "
                    f"{suffix} do not add up to records of {record} bytes"
                )
            # a line without a pixel count
            if samples is None:
                # holds as many pixels as its samples have room for
                samples, remainder = divmod(layout.data, group)
                # which must be a whole number of them
                if remainder:
                    # otherwise the pixels are not what the descriptor says
                    return self._complain(
                        f"{layout.data} bytes of samples do not hold pixels of {group} bytes"
                    )
        # without the bytes of samples, the samples end right before the suffix
        elif samples is not None:
            # so they start where the pixels of the line leave off
            start = record - suffix - samples * group
            # which must be past the record header
            if start < 12:
                # otherwise the pixels do not fit
                return self._complain(f"{samples} pixels do not fit in records of {record} bytes")
        # without either
        else:
            # the lines cannot be found
            return self._complain(
                "the descriptor says neither the pixels nor the samples of a line"
            )
        # the samples of a line must fit in its record
        if start + samples * group + suffix > record:
            # otherwise they run into the next one
            return self._complain(f"{samples} pixels do not fit in records of {record} bytes")
        # the records of a line
        if layout.recordsPerLine not in (None, 1):
            # must be one, or each line is split across records
            return self._complain(f"lines split across {layout.recordsPerLine} records")
        # the lines of each channel: the descriptor, or all the records
        lines = layout.lines if layout.lines else records
        # the number of channels, from the records, since the channel count is not always right
        channels, remainder = divmod(records, lines)
        # the records must hold whole channels
        if remainder or not channels:
            # otherwise the lines are not what the descriptor says
            return self._complain(f"{records} records do not hold channels of {lines} lines")
        # the interleave of the channels, which matters only when there is more than one
        interleave = (layout.interleave or "BSQ").strip().upper()
        # and must be one i know
        if channels > 1 and interleave not in ("BSQ", "BIL"):
            # otherwise the channels cannot be found
            return self._complain(f"unsupported interleave '{interleave}'")
        # the cell type
        cell = self._cell(code=layout.code, group=group)
        # without one
        if cell is None:
            # the complaint has been lodged
            return None
        # assemble the layout
        return types.SimpleNamespace(
            descriptor=descriptor,
            record=record,
            start=start,
            lines=lines,
            samples=samples,
            channels=channels,
            interleave=interleave,
            cell=cell,
        )

    def _cell(self, code, group):
        """
        Build the specification of the cell type from the format type {code} and the bytes per
        pixel {group}; the size comes from {group}, since producers do not agree on what the
        size in the code means
        """
        # normalize the code
        code = (code or "").strip().upper()
        # the name of the cell type, when the code and the size make one i can read
        name = None
        # complex floats
        if code.startswith("C*") and group == 8:
            # two single precision parts
            name = "complex64"
        # unsigned integers, or no code at all, which the producers use for bytes and shorts
        elif code.startswith(("IU", "UI")) or not code:
            # of the size of a pixel
            name = {1: "uint8", 2: "uint16"}.get(group)
        # real floats
        elif code.startswith("R*") and group == 4:
            # in single precision
            name = "float32"
        # anything else
        if name is None:
            # is not supported yet
            return self._complain(
                f"unsupported sample format '{code}' with {group} bytes per pixel"
            )
        # single byte cells have no byte order
        if group == 1:
            # so the name will do
            return name
        # all multi-byte samples in CEOS files are big endian
        return ">" + name

    def _fields(self, record):
        """
        Extract the layout fields from the file descriptor {record}; the positions are the 1-based
        byte ranges of the CEOS SAR image file descriptor
        """

        # read a field as an integer, or {None} when it is blank
        def number(first, last):
            # the text of the field
            text = record[first - 1 : last].decode("ascii", errors="replace").strip()
            # a blank field says nothing
            if not text:
                # so leave it unset
                return None
            # carefully
            try:
                # convert it
                return int(text)
            # a field that does not hold a number
            except ValueError:
                # says nothing either
                return None

        # read a field as text
        def text(first, last):
            # decode it
            return record[first - 1 : last].decode("ascii", errors="replace").strip()

        # collect the fields
        return types.SimpleNamespace(
            # the number of data records, and the length of each one
            records=number(181, 186),
            record=number(187, 192),
            # the bytes of each pixel
            group=number(225, 228),
            # the lines of each channel
            lines=number(237, 244),
            # the border pixels on the left, the pixels of each line, and the border on the right
            left=number(245, 248),
            pixels=number(249, 256),
            right=number(257, 260),
            # the interleave of the channels
            interleave=text(269, 272),
            # the records of each line
            recordsPerLine=number(273, 274),
            # the bytes of each record in front of the samples, of the samples, and after them
            prefix=number(277, 280),
            data=number(281, 288),
            suffix=number(289, 292),
            # the format type code of the samples
            code=text(429, 432),
        )

    @staticmethod
    def _header(header):
        """
        Unpack the sequence number, the type bytes, and the length of the record whose 12 byte
        {header} is given
        """
        # the sequence number and the length are big endian unsigned integers around the type
        sequence, kind, length = struct.unpack(">I4sI", header)
        # hand them back
        return sequence, kind, length

    def _complain(self, *reasons):
        """
        Report that the image file cannot be read, and why
        """
        # make a channel
        channel = journal.error("qed.readers.native.ceos")
        # complain
        channel.line(f"could not load a dataset from '{self.uri.address}'")
        # go through the reasons
        for reason in reasons:
            # and show each one
            channel.line(reason)
        # flush
        channel.log()
        # and bail
        return None

    # private data
    _layout = None  # the layout of the raster, once read


# end of file
