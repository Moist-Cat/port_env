port-env
===================================

# What problem does this software solve

Python virtual environments are not portable because paths are hard-coded in all the scripts at /bin. Also, the third party libraries aren't found if you change versions even if they are compatible.
This command line utility wraps a few of the main GNU coreutils (awk, sed) to fix these things.

# Requirements

1. sed, awk
2. python3 (no third party dependencies are needed for now)

# Install
From pipy

    pip install port_env

From source

    python setup.py bdist_wheel
    pip install dist/*

# Quick Guide

    port_env [ENV]

You can use the --third_party=1 flag to also move lib/python3.* and rename it to the current python version. It's optional because this might not be what you want if you have several versions of python installed.
