// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "externals.h"
// the namespace and its forward declarations
#include "forward.h"


// a pipeline decorator that paints the cells where a raster has nothing to say
template <class sourceT, class pipelineT>
class qed::nisar::Absence {
    // types
public:
    // me
    using self_type = Absence<sourceT, pipelineT>;
    // the raster i watch, and the pipeline whose colors i pass through
    using source_type = sourceT;
    using pipeline_type = pipelineT;
    // what my sources hand me
    using source_reference = typename source_type::reference;
    // the colors i produce, which are the ones my pipeline produces
    using rgb_type = typename pipeline_type::rgb_type;
    // and what a fill value is spelled as: the magnitude of the cell the product declared,
    // because a fill is a fill whatever the parts of a complex number happen to be
    using fill_type = double;

    // metamethods
public:
    // build one out of the raster, the pipeline that colors it, and what the product says
    // it writes where it has nothing to record
    inline Absence(source_type source, pipeline_type pipeline, fill_type fill);

    // the full set, declared explicitly
    Absence(const Absence &) = default;
    Absence(Absence &&) = default;
    Absence & operator=(const Absence &) = default;
    Absence & operator=(Absence &&) = default;
    ~Absence() = default;

    // interface
public:
    // the color of the current cell
    inline auto operator*() const -> rgb_type;
    // advance everything i draw from
    inline auto operator++() -> void;

    // implementation details
private:
    // the raster, which i read for its raw value
    source_type _source;
    // the pipeline that knows what color a measurement should be
    pipeline_type _pipeline;
    // the magnitude of the value the product declared as its fill
    fill_type _fill;

    // constants
private:
    // a cell holding exactly what the product declared it would write where it has nothing
    // to say. the masked channels already paint their out-of-swath margin this faint brick
    // red, so absence looks the same whether a mask or the fill value announced it
    static constexpr rgb_type declared = { 0.10, 0.05, 0.05 };
    // a cell holding a nan the product never declared. this is worth seeing rather than
    // hiding: a raster whose empty cells disagree with its own fill value is a bug in
    // whatever wrote it, and there is no way to tell from the metadata alone
    static constexpr rgb_type undeclared = { 0.04, 0.11, 0.10 };
};


// pull in the implementation
#include "Absence.icc"


// end of file
