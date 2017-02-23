gns-deb-diff
============

A script that generates differences between gNewSense and Debian.

source
------

::

   git clone git://git.ricketyspace.net/gns-deb-diff.git

development environment
-----------------------

::

   cd gns-deb-diff
   virtualenv --python=python3 .
   source activate
   pip install -r requirements.txt
   python setup develop

installation
------------

::

   pip install gns-deb-diff

usage
-----

::

   gd-diff RELEASE RELEASE_NUMBER

config
------

::

   {
       "user": "sddhrth",
       "pass": "weasaspeciesarenicelyfckd"
   }


config directory structure
--------------------------

::

   ~/.config/gns-deb-diff/
       config  # json format
       pkgs/
           parkes # \n seperated list o' pkgs
           ucclia
       readmes/
           parkes/
               pkg-foo/debian/README.gNewSense
               pkg-bar/debian/README.gNewSense
               .
               .
           ucclia/
               pkg-foo/debian/README.gNewSense
               pkg-bar/debian/README.gNewSense
               .
               .
       wiki-page/
           parkes/
               wiki.page # contains latest generated page.
           ucclia/
               wiki.page

license
-------

Under `Public Domain`__.

.. _cc0: https://creativecommons.org/publicdomain/zero/1.0
__ cc0_
