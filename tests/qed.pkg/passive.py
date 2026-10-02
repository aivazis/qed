#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that construction is passive: every reader, archive, and workspace can be configured and
built without touching the filesystem or the network, the application can be built without
building the state it manages, and building that state later still opens no product and mounts
no archive
"""

# externals
import sys

# support
import journal
import pyre
import qed

# the readers complain about the missing web documents; this driver is not the app
journal.warning("qed.cli").deactivate()

# the audit events that touch the filesystem
filesystem = {
    "open",
    "os.listdir",
    "os.scandir",
    "os.mkdir",
    "os.remove",
    "os.rmdir",
    "os.rename",
    "os.chdir",
    "os.truncate",
    "os.utime",
    "mmap.__new__",
    "shutil.rmtree",
}
# the audit events that touch the network or other processes
network = {
    "socket.connect",
    "socket.bind",
    "socket.getaddrinfo",
    "socket.gethostbyname",
    "socket.gethostbyaddr",
    "urllib.Request",
    "subprocess.Popen",
    "os.system",
    "os.posix_spawn",
    "os.exec",
}
# the prefix of the installed packages, where modules imported on first use come from
installed = str(pyre.primitives.path(pyre.__file__).parent.parent)

# what happened while the hook was armed, as (phase, event, arguments) triples
touched = []
# the phase being watched; nothing is recorded outside of one
phase = None


def hook(event, args):
    """
    Record the events that touch the filesystem or the network while a phase is being watched
    """
    # outside of a phase
    if phase is None:
        # nothing is recorded
        return
    # if the event is of interest
    if event in filesystem or event in network:
        # record it
        touched.append((phase, event, args))
    # all done
    return


def spy(module, name):
    """
    Replace the callable {name} in {module} with one that records its calls as events
    """
    # get the original
    original = getattr(module, name)

    # the replacement
    def spied(*args, **kwds):
        """
        Record the call and then make it
        """
        # if a phase is being watched
        if phase is not None:
            # record the call
            touched.append((phase, f"{module.__name__}.{name}", args))
        # and make it
        return original(*args, **kwds)

    # install it
    setattr(module, name, spied)
    # all done
    return


def compiled(event, args):
    """
    Check whether an event reads a compiled module from the installation, which is what
    importing a module on first use does
    """
    # only opens qualify
    if event != "open":
        # so nothing else does
        return False
    # get the path
    path = str(args[0])
    # a compiled module in the installation
    return path.startswith(installed) and path.endswith(".pyc")


def configuration(event, args):
    """
    Check whether an event reads a configuration file, which is what configuring does
    """
    # only opens qualify
    if event != "open":
        # so nothing else does
        return False
    # get the path
    path = str(args[0])
    # a file in one of the configuration formats
    return path.endswith((".yaml", ".pfg", ".cfg", ".toml", ".ini"))


def watch(name, build):
    """
    Invoke {build} while watching for events under the phase {name}, and hand back the result
    """
    # access the phase marker
    global phase
    # arm the hook
    phase = name
    # carefully, so the hook is disarmed no matter what
    try:
        # build
        product = build()
    # when done
    finally:
        # disarm the hook
        phase = None
    # hand back what was built
    return product


def strays(allowed):
    """
    Collect the recorded events that {allowed} does not excuse, and forget all of them
    """
    # the ones that are not excused
    found = [
        (name, event, args) for name, event, args in touched if not allowed(event=event, args=args)
    ]
    # forget everything
    touched.clear()
    # hand off the rest
    return found


# watch the native entry points, which do their work where the audit hook cannot see it: the
# products opened through the h5 layer
spy(module=pyre.h5, name="read")
spy(module=pyre.h5, name="reader")
# the flat files mapped into memory
spy(module=qed.libpyre.grid, name="map")
# carefully, since these are optional
try:
    # the products opened through GDAL
    from osgeo import gdal
# if it is not there
except ImportError:
    # there is nothing to watch
    pass
# otherwise
else:
    # watch it
    spy(module=gdal, name="Open")
# carefully
try:
    # the sessions with AWS
    import boto3
# if it is not there
except ImportError:
    # there is nothing to watch
    pass
# otherwise
else:
    # watch it
    spy(module=boto3, name="Session")

# install the hook
sys.addaudithook(hook)


# the products the readers are pointed at, none of which exists
uris = {
    "file": "file:/nonexistent/qed/product.h5",
    "s3": "s3://nonexistent-bucket/qed/product.h5",
}
# the readers
readers = {
    "nisar.rrsd": qed.readers.nisar.rrsd,
    "nisar.rslc": qed.readers.nisar.rslc,
    "nisar.roff": qed.readers.nisar.roff,
    "nisar.rifg": qed.readers.nisar.rifg,
    "nisar.runw": qed.readers.nisar.runw,
    "nisar.gslc": qed.readers.nisar.gslc,
    "nisar.goff": qed.readers.nisar.goff,
    "nisar.gunw": qed.readers.nisar.gunw,
    "nisar.gcov": qed.readers.nisar.gcov,
    "nisar.l0a": qed.readers.nisar.l0a,
    "nisar.h5": qed.readers.nisar.h5,
    "isce2.slc": qed.readers.isce2.slc,
    "isce2.int": qed.readers.isce2.int,
    "isce2.unw": qed.readers.isce2.unw,
    "native.flat": qed.readers.native.flat,
    "native.envi": qed.readers.native.envi,
    "asar.rslc": qed.readers.asar.rslc,
}
# carefully, since GDAL is optional
try:
    # get the reader
    readers["native.gdal"] = qed.readers.native.gdal()
# if it is not there
except ImportError:
    # there is nothing to check
    pass

# go through the readers
for tag, factory in readers.items():
    # and the kinds of location
    for kind, uri in uris.items():
        # build one
        watch(
            name=f"reader {tag} at a {kind} location",
            build=lambda: factory(name=f"passive.{tag}.{kind}", uri=uri),
        )
# build a stack of two
watch(
    name="stack",
    build=lambda: qed.stacks.stack(
        name="passive.stack",
        readers=[
            qed.readers.nisar.gunw(name="passive.stack.bucket", uri=uris["s3"]),
            qed.readers.nisar.gunw(name="passive.stack.file", uri=uris["file"]),
        ],
    ),
)
# build a local archive at a folder that does not exist
local = watch(
    name="local archive",
    build=lambda: qed.archives.local(name="passive.local", uri="file:/nonexistent/qed"),
)
# an archive in a bucket that does not exist, under a profile that does not exist
bucket = watch(
    name="s3 archive",
    build=lambda: qed.archives.s3(
        name="passive.s3",
        uri="s3://nonexistent-bucket/qed",
        profile="nonexistent",
        region="us-west-2",
    ),
)
# an earth archive
watch(
    name="earth archive",
    build=lambda: qed.archives.earth(name="passive.earth", uri="earth:passive"),
)
# and a workspace in a folder that does not exist
watch(
    name="workspace",
    build=lambda: qed.workspaces.local(name="passive.workspace", path="/nonexistent/qed/ws"),
)
# none of them touched anything but the modules they imported on first use
found = strays(allowed=compiled)
assert not found, "\n".join(f"{name}: {event} {args}" for name, event, args in found)
# and the archives have mounted nothing
assert local.fs is None and bucket.fs is None


# build the application, with an archive and a product in a bucket
app = watch(
    name="application",
    build=lambda: qed.shells.qed(
        name="passive.app",
        archives=["qed.archives.s3#passive.app.bucket"],
        datasets=["qed.readers.nisar.gunw#passive.app.product"],
    ),
)


# while configuring, the framework reads its configuration and mounts its filespace, which
# lists and creates folders; what it may never do is read anything else or reach the network
def configuring(event, args):
    """
    Excuse what the framework does while it configures an application
    """
    # the modules imported on first use and the configuration files
    if compiled(event=event, args=args) or configuration(event=event, args=args):
        # are fine
        return True
    # and so is the mounting of the filespace
    return event in {"os.listdir", "os.scandir", "os.mkdir"}


# check
found = strays(allowed=configuring)
assert not found, "\n".join(f"{name}: {event} {args}" for name, event, args in found)
# the application built none of the state it manages
assert app._ux is None

# build the dispatcher by hand, since this driver has no web documents to find
ux = watch(
    name="dispatcher",
    build=lambda: qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs),
)
# which built the store and everything it manages without touching anything
found = strays(allowed=compiled)
assert not found, "\n".join(f"{name}: {event} {args}" for name, event, args in found)
# including the archive in the bucket, which has not been mounted
archives = {archive.pyre_name: archive for archive in ux.store._dataArchives.archives()}
assert archives["passive.app.bucket"].fs is None


# end of file
