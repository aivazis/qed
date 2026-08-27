# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the accumulator of whole-dataset statistics
class Sample:
    """
    A mergeable accumulator of dataset statistics

    Workers ship per-tile records of the form (count, min, mean, m2, max) over the magnitude
    of the source values; this accumulator folds them together using the parallel form of
    Welford's update, so the running statistics are exact regardless of arrival order
    """

    # interface
    def merge(self, record: tuple) -> "Sample":
        """
        Fold the per-tile {record} into my running statistics
        """
        # unpack the record
        count, low, mean, m2, high = record
        # an empty record, e.g. from a tile of nothing but nans
        if count == 0:
            # contributes nothing
            return self
        # count the contribution
        self.tiles += 1
        # if this is the first real record
        if self.count == 0:
            # it becomes the running state
            self.count = count
            self.min = low
            self.mean = mean
            self.m2 = m2
            self.max = high
            # all done
            return self
        # otherwise, form the combined population size
        total = self.count + count
        # the distance between the two means
        delta = mean - self.mean
        # fold in the second moment, a la Chan et al.
        self.m2 += m2 + delta**2 * self.count * count / total
        # shift the mean by the record's weighted contribution
        self.mean += delta * count / total
        # update the population size
        self.count = total
        # and the extrema
        self.min = min(self.min, low)
        self.max = max(self.max, high)
        # all done
        return self

    @property
    def variance(self) -> float:
        """
        The variance of the accumulated sample
        """
        # the second moment over the population size, guarding against an empty sample
        return self.m2 / self.count if self.count > 0 else 0.0

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the number of records folded in
        self.tiles = 0
        # the population size
        self.count = 0
        # the extrema
        self.min = 0.0
        self.max = 0.0
        # the running mean and second moment
        self.mean = 0.0
        self.m2 = 0.0
        # all done
        return

    def __str__(self) -> str:
        # a compact rendering for the diagnostic channels
        return (
            f"tiles: {self.tiles}, count: {self.count:g}, "
            f"min: {self.min:g}, mean: {self.mean:g}, max: {self.max:g}, "
            f"variance: {self.variance:g}"
        )


# end of file
