# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal
import qed


# the base of the channels of the readers
class Channel(qed.flow.dynamic, implements=qed.protocols.channel):
    """
    The base of the channels of the readers: a channel renders the tiles of a dataset, either
    through the pipeline its recipe describes or through the fused iterators of its family
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
        # don't know what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'eval'")

    def project(self, pixel):
        """
        Compute the channel representation of a {pixel}
        """
        # don't know what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'project'")

    def recipe(self):
        """
        The pipeline that renders my tiles, from the rasters of a dataset to its image, or
        nothing when i have none and render with the iterators
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

    def cells(self, source) -> dict:
        """
        The buffers of the cells of {source} my recipe reads, by the name of the raster product
        that stands for each one
        """
        # by default, the whole dataset is the one raster
        return {"raster": source.data}

    def iterators(self, source, origin, shape, stride, **kwds):
        """
        Render the tile of {source} at {origin}+{shape}, at the given {stride}, with the fused
        iterators of my family
        """
        # my family must say how
        raise NotImplementedError(f"class {type(self).__name__} must implement 'iterators'")

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # turn the zoom levels into per-axis strides
        stride = tuple(2**level for level in zoom)
        # with the pipeline of my recipe, if i have one and was asked to use it
        if self.engine == "flow" and self.pipeline() is not None:
            # make rasters over the cells of the dataset
            rasters = self.rasters(source=source)
            # if all of them could be made
            if rasters is not None:
                # render through my pipeline
                return self.flow(rasters=rasters, origin=origin, shape=shape, stride=stride)
        # otherwise, render with the iterators
        return self.iterators(source=source, origin=origin, shape=shape, stride=stride, **kwds)

    def rasters(self, source) -> dict | None:
        """
        Make the rasters my recipe reads over the cells of {source}, by product name, or nothing
        when pyre::flow has no rasters of its cells
        """
        # the rasters
        rasters = {}
        # go through the buffers my recipe reads
        for name, cells in self.cells(source=source).items():
            # a raster shares the cells of its buffer rather than copies them; it is cheap, so it
            # is made for every tile, and a dataset that is rebuilt for every tile, the way the
            # blocks of a file of records are, costs no more than one that lasts
            try:
                # make one
                rasters[name] = qed.libpyre.flow.raster(
                    source=cells, name=f"{self.pyre_name}.{name}"
                )
            # cells pyre::flow has no rasters of, such as the ones in the byte order the host lacks
            except ValueError as error:
                # are rendered by the iterators
                channel = journal.debug("qed.channels.flow")
                # say so
                channel.log(f"'{self.pyre_name}' renders through the iterators: {error}")
                # and bail
                return None
        # hand them off
        return rasters

    def flow(self, rasters, origin, shape, stride):
        """
        Render the tile of {rasters} at {origin}+{shape}, at the given {stride}, through the
        pipeline of my recipe: staged once per combination of raster types, and realized once
        per combination and tile shape
        """
        # the types of the rasters, by product name
        decls = {name: raster.decl for name, raster in rasters.items()}
        # the combination, in a form that can key a table
        kinds = tuple(sorted(decls.items()))
        # the graph for this combination and the tile shape
        key = (kinds, tuple(shape))
        # look it up
        graph = self._graphs.get(key)
        # if this is the first tile of its kind
        if graph is None:
            # look up the plan for the combination
            plan = self._plans.get(kinds)
            # if there isn't one yet
            if plan is None:
                # stage my recipe, starting from the rasters
                plan = self.pipeline().stage(products=decls)
                # and remember it
                self._plans[kinds] = plan
            # realize the plan for the shape, around the rasters
            graph = plan.realize(shape=tuple(shape), nodes=rasters)
            # and remember it
            self._graphs[key] = graph
        # otherwise
        else:
            # the rasters of this dataset replace the ones of the last
            for name, raster in rasters.items():
                # go through the factories that read it
                for binding in self.pipeline().readers(product=name):
                    # each one reads the new raster from now on
                    if not graph[binding.factory].bind(slot=binding.slot, product=raster):
                        # a raster a factory refuses is a mismatch between my recipe and the code
                        channel = journal.firewall("qed.channels.flow")
                        # say so
                        channel.line(f"'{binding.factory}' of the recipe of '{self.pyre_name}'")
                        channel.log(f"refused the raster '{name}' of a dataset")
                        # and bail, in case firewalls are not fatal
                        return None
                # the graph keeps it alive, since the factories refer to it weakly
                graph.nodes[name] = raster
        # the window, counted in strides, goes to every slicer
        for factory in self.slicers():
            # the origin
            self.apply(graph=graph, factory=factory, setting="origin", value=tuple(origin))
            # and the stride
            self.apply(graph=graph, factory=factory, setting="stride", value=stride)
        # the settings my controllers impose
        for factory, values in self.settings().items():
            # one factory at a time
            for setting, value in values.items():
                # one setting at a time
                self.apply(graph=graph, factory=factory, setting=setting, value=value)
        # pull the image
        return graph["image"].read()

    def slicers(self) -> list:
        """
        The names of the factories of my recipe that cut tiles out of rasters
        """
        # the ones whose protocol is the slicer's
        return [
            node.name
            for node in self.pipeline().factories()
            if issubclass(node.protocol, qed.viz.slicer)
        ]

    def apply(self, graph, factory, setting, value):
        """
        Change the {setting} of {factory} in {graph} to {value}
        """
        # change it
        if not graph[factory].set(setting=setting, value=value):
            # a setting my recipe's factory refuses is a mismatch between my recipe and the code
            channel = journal.firewall("qed.channels.flow")
            # say so
            channel.line(f"'{factory}' of the recipe of '{self.pyre_name}'")
            channel.log(f"refused {setting}={value!r}")
            # and bail, in case firewalls are not fatal
            return
        # all done
        return

    # recipe pieces
    @staticmethod
    def head(recipe, raster="raster", signal="signal", slicer="slice"):
        """
        Put the {slicer} at the head of {recipe}, cutting the {signal} out of the {raster}
        """
        # the slicer
        recipe.factory(name=slicer, protocol=qed.viz.slicer)
        # the raster it reads, and the signal it writes
        recipe.product(name=raster)
        recipe.product(name=signal)
        # wire it
        recipe.bind(factory=slicer, slot="source", product=raster)
        recipe.bind(factory=slicer, slot="slice", product=signal)
        # all done
        return recipe

    @classmethod
    def paint(cls, recipe, data):
        """
        Paint the product {data} of {recipe}, which holds values in [0, 1], gray, into the
        {image}
        """
        # the colormap
        recipe.factory(name="gray", protocol=qed.viz.colormap, pin=qed.viz.colormaps.gray())
        # wire its input
        recipe.bind(factory="gray", slot="data", product=data)
        # and encode its colors
        return cls.encode(recipe=recipe, colormap="gray")

    @classmethod
    def gray(cls, recipe, signal):
        """
        Normalize the product {signal} of {recipe} and paint it gray, into the {image}
        """
        # the normalizer
        recipe.factory(name="normalizer", protocol=qed.viz.normalizer)
        # the values it makes
        recipe.product(name="normalized")
        # wire it
        recipe.bind(factory="normalizer", slot="signal", product=signal)
        recipe.bind(factory="normalizer", slot="normalized", product="normalized")
        # and paint them
        return cls.paint(recipe=recipe, data="normalized")

    @staticmethod
    def turn(recipe, signal):
        """
        Place the phase of the product {signal} of {recipe} in its interval and map it onto the
        {hues}
        """
        # the phase, placed in its interval
        recipe.factory(name="cycle", protocol=qed.viz.filter, pin=qed.viz.filters.cycle())
        # mapped onto the hues
        recipe.factory(name="hue", protocol=qed.viz.filter, pin=qed.viz.filters.affine())
        # the products
        recipe.product(name="phases")
        recipe.product(name="hues")
        # the bindings
        recipe.bind(factory="cycle", slot="signal", product=signal)
        recipe.bind(factory="cycle", slot="cycle", product="phases")
        recipe.bind(factory="hue", slot="signal", product="phases")
        recipe.bind(factory="hue", slot="affine", product="hues")
        # all done
        return recipe

    @staticmethod
    def encode(recipe, colormap):
        """
        Encode the color channels the {colormap} of {recipe} makes into the {image}
        """
        # the encoder
        recipe.factory(name="encoder", protocol=qed.viz.encoder)
        # the products
        for name in ("red", "green", "blue", "image"):
            # one at a time
            recipe.product(name=name)
        # the bindings
        for factory, slot, product in [
            (colormap, "red", "red"),
            (colormap, "green", "green"),
            (colormap, "blue", "blue"),
            ("encoder", "red", "red"),
            ("encoder", "green", "green"),
            ("encoder", "blue", "blue"),
            ("encoder", "image", "image"),
        ]:
            # one at a time
            recipe.bind(factory=factory, slot=slot, product=product)
        # all done
        return recipe

    @classmethod
    def wheel(cls, recipe, signal, brightness):
        """
        Paint the phase of the product {signal} of {recipe} as a hue, with a constant saturation
        and the product {brightness} as the brightness, into the {image}
        """
        # turn the phase into hues
        cls.turn(recipe=recipe, signal=signal)
        # a constant saturation
        recipe.factory(name="saturation", protocol=qed.viz.filter, pin=qed.viz.filters.constant())
        recipe.product(name="saturations")
        recipe.bind(factory="saturation", slot="tile", product="saturations")
        # the colormap
        recipe.factory(name="hsb", protocol=qed.viz.colormap, pin=qed.viz.colormaps.hsb())
        # wire its inputs
        recipe.bind(factory="hsb", slot="hue", product="hues")
        recipe.bind(factory="hsb", slot="saturation", product="saturations")
        recipe.bind(factory="hsb", slot="brightness", product=brightness)
        # and encode its colors
        return cls.encode(recipe=recipe, colormap="hsb")

    @classmethod
    def light(cls, recipe, hues, luminosity):
        """
        Paint the product {hues} of {recipe} as a hue, with the product {luminosity} as the
        luminosity, into the {image}
        """
        # the colormap
        recipe.factory(name="hl", protocol=qed.viz.colormap, pin=qed.viz.colormaps.hl())
        # wire its inputs
        recipe.bind(factory="hl", slot="hue", product=hues)
        recipe.bind(factory="hl", slot="luminosity", product=luminosity)
        # and encode its colors
        return cls.encode(recipe=recipe, colormap="hl")

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
        # the plans of my recipe, by the types of the rasters they start from
        self._plans = {}
        # and the graphs they realized, by the types of the rasters and the tile shape
        self._graphs = {}
        # all done
        return


# end of file
