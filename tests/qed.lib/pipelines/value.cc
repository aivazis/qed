// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
#include <cassert>
#include <cmath>
#include <cstring>
#include <string>
// support
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/memory.h>
#include <pyre/timers.h>
// the code under test
#include <qed/native.h>


// type aliases
// the cells of the source
using cell_t = float;
// the source: a dense grid on the heap
using packing_t = pyre::grid::canonical_t<2>;
using storage_t = pyre::memory::heap_t<cell_t>;
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;
// its indices and shapes
using index_t = grid_t::index_type;
using shape_t = grid_t::shape_type;
// the pipeline under test
using pipeline_t = qed::native::pipelines::Value;
// the clocks
using timer_t = pyre::timers::wall_timer_t;


// render the value of the same tiles with the iterators and with the flow pipeline, check that
// they encode the same bytes, and time both, along with the stages of the pipeline; the timings
// go to the debug channel {qed.native.pipelines.timing}, so the run is silent unless asked, e.g.
//     value --journal.debug=qed.native.pipelines.timing
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");
    // the channel for the timings
    auto report = pyre::journal::debug_t("qed.native.pipelines.timing");

    // the extent of the source
    const int rows = 4096;
    const int columns = 4096;
    // the source
    auto source = grid_t(packing_t(shape_t { rows, columns }), rows * columns);
    // go through its cells
    for (auto row = 0; row < rows; ++row) {
        // and the cells of each line
        for (auto column = 0; column < columns; ++column) {
            // fill it with a smooth field that spills beyond the interval at both ends
            source[{ row, column }] = 2.0 * std::sin(row / 97.0) * std::cos(column / 131.0) + 0.5;
        }
    }
    // the interval that is mapped onto [0,1]
    const double low = 0.0;
    const double high = 1.5;
    // the number of timed renders of each tile
    const int trials = 20;

    // the pipeline, which keeps a graph per tile shape
    auto pipeline = pipeline_t();
    // the names of the clocks of its stages
    const std::string stages[] = { "copy", "normalize", "paint", "encode" };

    // the header of the report
    report
        // where
        << pyre::journal::at()
        // the columns, in milliseconds per tile
        << "span zoom  iterators   flow  build |   copy normalize  paint encode   (ms per tile)"
        << pyre::journal::newline;

    // go through the tile sizes
    for (auto span : { 128, 256, 512 }) {
        // and the zoom levels
        for (auto zoom : { 0, 1, 2 }) {
            // the stride of this level
            const int stride = 1 << zoom;
            // the tile, in decimated cells, in the middle of the source
            auto origin = index_t { (rows / stride - span) / 2, (columns / stride - span) / 2 };
            auto shape = shape_t { span, span };
            auto step = index_t { stride, stride };

            // the clock of the iterators
            auto iterators = timer_t("qed.native.pipelines.harness.iterators");
            // reset it
            iterators.reset();
            // render the tile with the iterators, keeping the last image
            auto expected = qed::native::channels::value(source, origin, shape, step, low, high);
            // and then time it
            for (auto trial = 0; trial < trials; ++trial) {
                // start the clock
                iterators.start();
                // render
                expected = qed::native::channels::value(source, origin, shape, step, low, high);
                // stop the clock
                iterators.stop();
            }

            // the clock of the first render with the flow, which builds the graph for this shape
            auto build = timer_t("qed.native.pipelines.harness.build");
            // reset it
            build.reset();
            // render once, untimed by the stages
            build.start();
            pipeline.render(source, origin, shape, step, low, high);
            build.stop();
            // reset the clocks of the stages, so they only count the timed renders
            for (const auto & stage : stages) {
                // by name
                timer_t("qed.native.pipelines.value." + stage).reset();
            }
            // the clock of the flow
            auto flow = timer_t("qed.native.pipelines.harness.flow");
            // reset it
            flow.reset();
            // the image of the last render
            auto image = pipeline.render(source, origin, shape, step, low, high);
            // reset the stages once more, since that render was a warm one, not a timed one
            for (const auto & stage : stages) {
                // by name
                timer_t("qed.native.pipelines.value." + stage).reset();
            }
            // time the renders
            for (auto trial = 0; trial < trials; ++trial) {
                // start the clock
                flow.start();
                // render
                image = pipeline.render(source, origin, shape, step, low, high);
                // stop the clock
                flow.stop();
            }

            // the two images must be the same size
            assert(image.cells() == static_cast<std::size_t>(expected.bytes()));
            // and hold the same bytes
            assert(std::memcmp(image.data(), expected.data(), image.cells()) == 0);

            // the cost per tile of each clock
            auto perTile = [trials](double ms) -> double {
                // averaged over the trials
                return ms / trials;
            };
            // report
            report
                // the tile
                << span << " " << zoom
                << "   "
                // the strategies
                << perTile(iterators.ms()) << " " << perTile(flow.ms()) << " " << build.ms()
                << " | "
                // the stages of the flow
                << perTile(timer_t("qed.native.pipelines.value.copy").ms()) << " "
                << perTile(timer_t("qed.native.pipelines.value.normalize").ms()) << " "
                << perTile(timer_t("qed.native.pipelines.value.paint").ms()) << " "
                << perTile(timer_t("qed.native.pipelines.value.encode").ms())
                << pyre::journal::newline;
        }
    }
    // flush the report
    report << pyre::journal::endl;

    // all done
    return 0;
}


// end of file
