## -*- docker-image-name: "qed:noble-clang" -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved

# based on ubuntu
FROM ubuntu:noble

# set up some build variables
ARG instance=dev/micromamba/noble-clang
# python version
ARG python_version=3.13
ARG python=python${python_version}
# locations
ARG prefix=/usr/local
ARG srcdir=${prefix}/src
# the build system
ARG mm="${python} ${srcdir}/mm/mm.py"

# environment
# colorize (for fun)
ENV TERM=xterm-256color
# set up the dynamic linker path
ENV LD_LIBRARY_PATH=${prefix}/lib
# export the python choice
ENV PYTHON=${python}
# and the path to {mm}
ENV MM=${mm}


# update the package repository
RUN apt update -y
# get the latest
RUN apt dist-upgrade -y

# install the base software stack
RUN DEBIAN_FRONTEND=noninteractive \
        apt install -y \
        curl

# install micromamba and set up the environment
WORKDIR /root/.local
# make the bin directory
RUN mkdir -p bin
# fetch the latest
RUN curl "https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-linux-$(uname -m)" -o bin/micromamba -fsSL --compressed
# make it executable
RUN chmod +x bin/micromamba
# copy the environment configuration file
COPY etc/docker/${instance}/qed.yaml qed.yaml
# create the qed environment
RUN /root/.local/bin/micromamba env create --quiet --yes --file qed.yaml --prefix=/root/.local/envs/qed

# setup the interactive environment
# go home
WORKDIR /root
# copy the files with support for interactive use
COPY etc/docker/${instance}/inputrc .inputrc
# the startup file
COPY etc/docker/${instance}/bashrc bashrc.in
# expand
RUN sed \
        -e "s:@SRCDIR@:${srcdir}:g" \
        bashrc.in > .bashrc
# clean up
RUN rm bashrc.in

# copy the prompt
COPY etc/docker/${instance}/prompt.py prompt.py.in
# expand
RUN sed \
        -e "s:@INSTANCE@:${instance}:g" \
        prompt.py.in > prompt.py
# clean up
RUN rm prompt.py.in

# make the pyre configuration directory
WORKDIR /root/.pyre
# get the {mm} configuration file
COPY etc/docker/${instance}/mm.yaml mm.yaml.in
# expand
RUN sed \
        -e "s:@PYTHON_VERSION@:${python_version}:g" \
        mm.yaml.in > mm.yaml
# clean up
RUN rm mm.yaml.in

# place the {mm} control file
WORKDIR /root/.mm
# copy the relevant configuration file
COPY etc/docker/${instance}/config.mm config.mm.in
# expand
RUN sed \
        -e "s:@PYTHON_VERSION@:${python_version}:g" \
        config.mm.in > config.mm
# clean up
RUN rm config.mm.in

# go to the source directory
WORKDIR /usr/local/src


# end of file
