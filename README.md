Mypy stub generator
===================

Mypy requires stub files describing the interfaces of modules
in order to type-check code that uses them. Writing them is quite tedious
so here are some tools to help:

*   `stub.py` generates a dynamically typed stub file for a named
    module

*   `lsmod.py` gets a list of modules to stub by scraping the module
    index page on docs.python.org (not ideal, I know)

Requirements
------------

*   CPython version 3
*   Beautiful Soup version 4 if you want to run `lsmod.py`
    (get with `pip install beautifulsoup4`
           or `apt-get install python3-bs4`)

Usage
-----

Here's roughly what I did to get a mostly working set of stubs.

Decide what to stub:

    python3 lsmod.py > modules.txt

Generate the bulk of the stubs (assuming zsh):

    for m (`cat modules.txt`) python3 stub.py $m stubs

A couple didn't quite work with the default settings:

    rm stubs/{os,tempfile}.py
    python3 stub.py os stubs --force-package \
        --hiding MutableMapping --hiding _Environ
    python3 stub.py tempfile stubs --hiding _Random

I had to use the original hand-written stubs for another two:

*   `builtins` because the generated stub has some syntax errors
    around the definitions of `any` and `object`

*   `re` because the original stub had some extra interfaces
    (`Match` and `Pattern`, I think) which aren't actually exposed
    as classes in the python module.
