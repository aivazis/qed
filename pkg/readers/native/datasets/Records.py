# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import math
import struct
import sys
import types

# support
import journal
import qed

# superclass
from .MemoryMap import MemoryMap


# a dataset whose lines sit in the records of a file
class Records(MemoryMap, family="qed.datasets.native.records"):
    """
    A dataset whose lines sit one per record in a file, at a fixed distance from each other that
    need not be a multiple of the cell size, e.g. the image file of a CEOS product

    The file is mapped only for random access to its bytes. Every request copies the cells it
    needs out of the records into a dense block that is laid out the way the tile generators
    expect, so the generators never see the records at all
    """

    # public data
    record = qed.properties.int()
    record.default = None
    record.doc = "the number of bytes from the start of one line to the start of the next"

    # interface
    def profile(self, points, closed=False):
        """
        Sample my data along the path defined by {points}
        """
        # read the cells the path visits, in the order it visits them
        return [
            (line, sample, self._read(line=line, sample=sample))
            for line, sample in self._walk(points=points, closed=closed)
        ]

    def render(self, channel, zoom, origin, shape):
        """
        Render a tile of the given specification
        """
        # extract the lines of the tile, each holding every cell under the tile at full resolution
        block = self._block(zoom=zoom, origin=origin, shape=shape)
        # the lines are already decimated, so the channel decimates the columns only, starting at
        # the beginning of the block
        return channel.tile(
            source=types.SimpleNamespace(data=block),
            zoom=(0, zoom[1]),
            origin=(0, 0),
            shape=shape,
        )

    @qed.export
    def sample(self, zoom: tuple, origin: tuple, shape: tuple) -> tuple:
        """
        Collect a mergeable statistical sample of the tile at {origin}+{shape}, visiting
        exactly the decimated footprint the render at this {zoom} sees
        """
        # extract the block the render sees
        block = self._block(zoom=zoom, origin=origin, shape=shape)
        # sample it the way the render visits it: every line, and the columns at the zoom stride
        return qed.libqed.native.sample(
            source=block, origin=(0, 0), shape=shape, stride=(1, 2 ** zoom[1])
        )

    # implementation details
    def _open(self):
        """
        Map my file for random access to its bytes
        """
        # grab my uri
        uri = self.uri
        # only local files can be mapped
        if uri.scheme != "file":
            # make a channel
            channel = journal.error("qed.readers.native")
            # complain
            channel.line(f"while looking for {uri}")
            channel.line(f"unsupported scheme '{uri.scheme}' in the dataset URI")
            channel.line(f"the native reader supports local datasets only")
            # flush
            channel.log()
            # and bail
            return
        # blocks are laid out by casting their bytes to cells of the same width, and there is
        # no cast wider than eight bytes
        if self.cell.bytes not in self.widths:
            # make a channel
            channel = journal.error("qed.readers.native")
            # complain
            channel.line(f"while looking for {uri}")
            channel.line(f"{self.cell.cell} cells are too wide for a dataset laid out in records")
            # flush
            channel.log()
            # and bail
            return
        # the path to the file
        path = qed.primitives.path(uri.address)
        # my shape
        lines, samples = self.shape
        # the last byte my last line reaches
        required = self.offset + (lines - 1) * self.record + samples * self.cell.bytes
        # carefully, since the file may not be there
        try:
            # measure it
            actual = path.stat().st_size
        # if it is not
        except OSError as error:
            # make a channel
            channel = journal.error("qed.readers.native")
            # complain
            channel.line(f"while looking for '{path}'")
            channel.line(f"got: {error}")
            # flush
            channel.log()
            # and bail
            return
        # if the file does not reach it
        if actual < required:
            # make a channel
            channel = journal.error("qed.readers.native")
            # complain
            channel.line(f"'{path}' is too small for the declared layout")
            channel.line(f"{lines} lines of {samples} {self.cell.cell} cells, {self.record} bytes")
            channel.line(f"apart, past an offset of {self.offset} bytes, require {required} bytes")
            channel.line(f"but the file holds only {actual}")
            # flush
            channel.log()
            # and bail
            return
        # map the whole file as bytes, read-only, since qed never writes to a product
        return qed.libpyre.grid.map(
            uri=str(path), shape=(actual,), cell="uint8", create=False, writable=False
        )

    def _block(self, zoom, origin, shape):
        """
        Copy the cells under the tile at {origin}+{shape} at {zoom} into a dense block of
        {shape[0]} lines, each holding every cell under the tile at full resolution
        """
        # the zoom levels as strides
        scale = tuple(2**level for level in zoom)
        # my extent
        lines, samples = self.shape
        # the size of my cells
        size = self.cell.bytes
        # the cells of a line of the block
        columns = shape[1] * scale[1]
        # and its bytes
        width = columns * size
        # the block, zeroed, so any part of the tile that lies past my edges is blank
        block = bytearray(shape[0] * width)
        # the first column under the tile
        first = origin[1] * scale[1]
        # the bytes of each line that fall inside my extent
        span = max(0, min(samples, first + columns) - first) * size
        # the bytes of my file
        source = memoryview(self.data)
        # go through the lines of the block
        for row in range(shape[0]):
            # the line of mine it decimates to
            line = (origin[0] + row) * scale[0]
            # lines past my last one stay blank, and so do all that follow
            if line >= lines:
                # so stop
                break
            # where its cells start in my file
            start = self.offset + line * self.record + first * size
            # copy them into the block
            block[row * width : row * width + span] = source[start : start + span]
        # view the block as cells in my byte order, laid out as {shape[0]} lines of {columns}
        return qed.libpyre.grid.view(
            source=memoryview(block).cast(self.widths[size]),
            shape=(shape[0], columns),
            cell=self.cell.ordered,
            writable=False,
        )

    def _read(self, line, sample):
        """
        Read the cell at {line} and {sample}
        """
        # the size of my cells
        size = self.cell.bytes
        # where the cell starts in my file
        start = self.offset + line * self.record + sample * size
        # its bytes
        cell = bytes(memoryview(self.data)[start : start + size])
        # the byte order of my cells, as the struct module spells it
        order = (">" if sys.byteorder == "little" else "<") if self.cell.byteswap else "="
        # decode them
        value = struct.unpack(order + self.codes[self.cell.cell], cell)
        # a complex cell is a pair of parts
        if len(value) == 2:
            # which make one number
            return complex(*value)
        # everything else is a single value
        return value[0]

    def _walk(self, points, closed):
        """
        Generate the cells a profile along {points} visits, exactly the way the profile kernel in
        {lib/qed/native/profile.icc} visits them
        """
        # an empty path visits nothing
        if not points:
            # so there is nothing to do
            return
        # a path with more than one point is a chain of segments
        if len(points) > 1:
            # one between each point and the next
            segments = list(zip(points[:-1], points[1:]))
            # and one that returns to the start of a closed path
            if closed:
                # from its last point to its first
                segments.append((points[-1], points[0]))
            # go through them
            for tail, head in segments:
                # the number of steps along the segment, as the kernel counts them
                steps = max(abs(tail[0] - head[0] + 1), abs(tail[1] - head[1] + 1))
                # take them
                for step in range(steps):
                    # the offset of this step from the tail, rounded the way the kernel rounds
                    dx = self._round(step / steps * (head[0] - tail[0]))
                    dy = self._round(step / steps * (head[1] - tail[1]))
                    # visit the cell
                    yield tail[0] + dx, tail[1] + dy
        # the path ends at its last point, or back at its first when it is closed
        last = points[0] if closed else points[-1]
        # visit it
        yield last[0], last[1]
        # all done
        return

    @staticmethod
    def _round(value):
        """
        Round {value} to the nearest integer, with halves away from zero, the way {std::round}
        does
        """
        # round the magnitude and restore the sign
        return int(math.copysign(math.floor(abs(value) + 0.5), value))

    # constants
    # the unsigned struct codes of each cell size, for casting a block of bytes into cells of that
    # width before laying a grid over it
    widths = {1: "B", 2: "H", 4: "I", 8: "Q"}
    # the struct codes of the parts of each cell type
    codes = {
        "int8": "b",
        "uint8": "B",
        "int16": "h",
        "uint16": "H",
        "int32": "i",
        "uint32": "I",
        "int64": "q",
        "uint64": "Q",
        "float32": "f",
        "float64": "d",
        "complex64": "ff",
        "complex128": "dd",
    }


# end of file
