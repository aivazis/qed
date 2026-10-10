# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal
import qed


# a channel is visualization workflow
class Channel(qed.flow.dynamic, implements=qed.protocols.channel):
    """
    The base class for all channels
    """

    # configurable state
    engine = qed.properties.str()
    engine.default = "flow"
    engine.validators = qed.constraints.isMember("iterators", "flow")
    engine.doc = (
        "render with the fused iterators, or with the pipeline my recipe describes; a channel "
        "with no recipe always uses the iterators"
    )

    # constants
    tag = None

    # interface
    @classmethod
    def description(cls):
        """
        The flow that describes what i compute, for drawing my pipeline, or nothing when there is
        no description yet
        """
        # by default, there is none
        return None

    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # nothing to do
        return

    def controllers(self):
        """
        Generate the set of controllers that can manipulate my state
        """
        # by default, nothing
        return []

    def eval(self, pixel):
        """
        Extract the channel value from a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'rep'")

    def project(self, pixel):
        """
        Compute the channel representation of a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'rep'")

    def recipe(self):
        """
        The pipeline that renders my tiles, from the raster of a dataset to its image, or nothing
        when i have none and render with the iterators
        """
        # by default, there is none
        return None

    def pipeline(self):
        """
        My recipe, built the first time i am asked for it
        """
        # if i haven't built it yet
        if not self._built:
            # build it
            self._recipe = self.recipe()
            # and remember that i did
            self._built = True
        # hand it off
        return self._recipe

    def settings(self) -> dict:
        """
        The settings my controllers impose on the factories of my recipe, by factory
        """
        # by default, there are none
        return {}

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # turn the zoom levels into per-axis strides
        stride = tuple(2**level for level in zoom)
        # with the pipeline of my recipe, if i have one and was asked to use it
        if self.engine == "flow" and self.pipeline() is not None:
            # make a raster over the cells of the dataset, which shares them rather than copies them
            try:
                # it is cheap, so it is made for every tile, and a dataset that is rebuilt for every
                # tile, the way the blocks of a file of records are, costs no more than one that lasts
                raster = qed.libpyre.flow.raster(
                    source=source.data, name=f"{self.pyre_name}.raster"
                )
            # cells pyre::flow has no rasters of, such as the ones in the byte order the host lacks
            except ValueError as error:
                # are rendered by the iterators
                channel = journal.debug("qed.channels.native.flow")
                # say so
                channel.log(f"'{self.pyre_name}' renders through the iterators: {error}")
            # otherwise
            else:
                # render through my pipeline
                return self.flow(raster=raster, origin=origin, shape=shape, stride=stride)
        # get my name
        name = self.tag
        # look for the tile maker in {libqed}
        pipeline = getattr(qed.libqed.native.channels, name)
        # build the visualization pipeline and return it
        return pipeline(source=source.data, origin=origin, shape=shape, stride=stride, **kwds)

    def flow(self, raster, origin, shape, stride):
        """
        Render the tile of {raster} at {origin}+{shape}, at the given {stride}, through the
        pipeline of my recipe: staged once per cell type, and realized once per cell type and
        tile shape
        """
        # the graph for its cells and the tile shape
        key = (raster.decl, tuple(shape))
        # look it up
        graph = self._graphs.get(key)
        # if this is the first tile of its kind
        if graph is None:
            # look up the plan for the cells
            plan = self._plans.get(raster.decl)
            # if there isn't one yet
            if plan is None:
                # stage my recipe, starting from the raster
                plan = self.pipeline().stage(products={"raster": raster.decl})
                # and remember it
                self._plans[raster.decl] = plan
            # realize the plan for the shape, around the raster
            graph = plan.realize(shape=tuple(shape), nodes={"raster": raster})
            # and remember it
            self._graphs[key] = graph
        # otherwise
        else:
            # the slice reads this dataset from now on
            if not graph["slice"].bind(slot="source", product=raster):
                # a raster the slice refuses is a mismatch between my recipe and the code
                channel = journal.firewall("qed.channels.native.flow")
                # say so
                channel.log(f"the slice of '{self.pyre_name}' refused the raster of a dataset")
                # and bail, in case firewalls are not fatal
                return None
            # and the graph keeps it alive, since the slice refers to it weakly
            graph.nodes["raster"] = raster
        # the window, counted in strides
        self.apply(graph=graph, factory="slice", setting="origin", value=tuple(origin))
        self.apply(graph=graph, factory="slice", setting="stride", value=stride)
        # the settings my controllers impose
        for factory, values in self.settings().items():
            # one factory at a time
            for setting, value in values.items():
                # one setting at a time
                self.apply(graph=graph, factory=factory, setting=setting, value=value)
        # pull the image
        return graph["image"].read()

    def apply(self, graph, factory, setting, value):
        """
        Change the {setting} of {factory} in {graph} to {value}
        """
        # change it
        if not graph[factory].set(setting=setting, value=value):
            # a setting my recipe's factory refuses is a mismatch between my recipe and the code
            channel = journal.firewall("qed.channels.native.flow")
            # say so
            channel.line(f"'{factory}' of the recipe of '{self.pyre_name}'")
            channel.log(f"refused {setting}={value!r}")
            # and bail, in case firewalls are not fatal
            return
        # all done
        return

    # recipe pieces
    @staticmethod
    def head(recipe):
        """
        Put a slice at the head of {recipe}, cutting the {signal} out of the {raster}
        """
        # the slicer
        recipe.factory(name="slice", protocol=qed.viz.slicer)
        # the raster it reads, and the signal it writes
        recipe.product(name="raster")
        recipe.product(name="signal")
        # wire it
        recipe.bind(factory="slice", slot="source", product="raster")
        recipe.bind(factory="slice", slot="slice", product="signal")
        # all done
        return recipe

    @staticmethod
    def gray(recipe, signal):
        """
        Paint the product {signal} of {recipe} gray, into the {image}
        """
        # the factories
        recipe.factory(name="normalizer", protocol=qed.viz.normalizer)
        recipe.factory(name="gray", protocol=qed.viz.colormap, pin=qed.viz.colormaps.gray())
        recipe.factory(name="encoder", protocol=qed.viz.encoder)
        # the products
        for name in ("normalized", "red", "green", "blue", "image"):
            # one at a time
            recipe.product(name=name)
        # the bindings
        for factory, slot, product in [
            ("normalizer", "signal", signal),
            ("normalizer", "normalized", "normalized"),
            ("gray", "data", "normalized"),
            ("gray", "red", "red"),
            ("gray", "green", "green"),
            ("gray", "blue", "blue"),
            ("encoder", "red", "red"),
            ("encoder", "green", "green"),
            ("encoder", "blue", "blue"),
            ("encoder", "image", "image"),
        ]:
            # one at a time
            recipe.bind(factory=factory, slot=slot, product=product)
        # all done
        return recipe

    @staticmethod
    def wheel(recipe, signal, brightness):
        """
        Paint the phase of the product {signal} of {recipe} as a hue, with a constant saturation
        and the product {brightness} as the brightness, into the {image}
        """
        # the factories: the phase, placed in its interval
        recipe.factory(name="cycle", protocol=qed.viz.filter, pin=qed.viz.filters.cycle())
        # mapped onto a full turn
        recipe.factory(name="hue", protocol=qed.viz.filter, pin=qed.viz.filters.affine())
        # a constant saturation
        recipe.factory(name="saturation", protocol=qed.viz.filter, pin=qed.viz.filters.constant())
        # the colormap
        recipe.factory(name="hsb", protocol=qed.viz.colormap, pin=qed.viz.colormaps.hsb())
        # and the encoder
        recipe.factory(name="encoder", protocol=qed.viz.encoder)
        # the products
        for name in ("phases", "hues", "saturations", "red", "green", "blue", "image"):
            # one at a time
            recipe.product(name=name)
        # the bindings
        for factory, slot, product in [
            ("cycle", "signal", signal),
            ("cycle", "cycle", "phases"),
            ("hue", "signal", "phases"),
            ("hue", "affine", "hues"),
            ("saturation", "tile", "saturations"),
            ("hsb", "hue", "hues"),
            ("hsb", "saturation", "saturations"),
            ("hsb", "brightness", brightness),
            ("hsb", "red", "red"),
            ("hsb", "green", "green"),
            ("hsb", "blue", "blue"),
            ("encoder", "red", "red"),
            ("encoder", "green", "green"),
            ("encoder", "blue", "blue"),
            ("encoder", "image", "image"),
        ]:
            # one at a time
            recipe.bind(factory=factory, slot=slot, product=product)
        # all done
        return recipe

    def update(self, **kwds):
        """
        Update the state of one of my controllers
        """
        # nothing for me to do
        return {}

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # my recipe, built on first use, which may be nothing
        self._recipe = None
        self._built = False
        # the plans of my recipe, by the type of the raster they start from
        self._plans = {}
        # and the graphs they realized, by the type of the raster and the tile shape
        self._graphs = {}
        # all done
        return


# end of file
