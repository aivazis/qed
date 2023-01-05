## -*- docker-image-name: "pyre:impish-gcc" -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved

# based on ubuntu
FROM ubuntu:impish

# set up some build variables
ARG instance=ci/impish-gcc
# python version
ARG python_version=3.9
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
        git vim zip unzip \
        openssh-server \
        g++ gfortran make \
        npm \
        ${python} ${python}-dev python3-numpy python3-pip python3-pybind11 python3-yaml \
        libgsl-dev libhdf5-dev \
        fftw3-dev


# install packages through pip
RUN pip3 install graphene

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
# copy the prompt
COPY etc/docker/${instance}/prompt.py prompt.py.in
# expand
RUN sed \
        -e "s:@INSTANCE@:${instance}:g" \
        prompt.py.in > prompt.py


# make the pyre configuration directory
WORKDIR /root/.pyre
# get the {mm} configuration file
COPY etc/docker/${instance}/mm.pfg mm.pfg.in
# expand
RUN sed \
        -e "s:@PREFIX@:${prefix}:g" \
        mm.pfg.in > mm.pfg

# place the {mm} control file
WORKDIR /root/.mm
# copy the relevant configuration file
COPY etc/docker/${instance}/config.mm config.mm.in
# expand
RUN sed \
        -e "s:@PYTHON_VERSION@:${python_version}:g" \
        config.mm.in > config.mm


# make the development area
WORKDIR ${srcdir}
# pull mm
RUN git clone https://github.com/aivazis/mm
# pull pyre
RUN git clone https://github.com/pyre/pyre
# pull qed
RUN git clone https://github.com/aivazis/qed

# go to the {pyre} top level directory
WORKDIR ${srcdir}/pyre
# build
RUN ${mm} --serial
# go to the {qed} top level directory
WORKDIR ${srcdir}/qed
# build
RUN ${mm} --serial


# end of file
