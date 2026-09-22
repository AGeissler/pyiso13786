pyiso13786 documentation
========================

pyiso13786 is an open, Python-based package providing methods for the calculation
procedures of ISO 13786:2017. The package includes some calculation procedures from
ISO 13788:2012. The package builds on the code by Nicola Meoli from the archive
https://github.com/sononicola/Static-and-Dynamic-thermal-characterics-of-buildings-components.

Changes/extensions include but are not restricted to the translation to english and the
addition of the class :py:class:`pyiso13786.space.Space`.

.. grid::

   .. grid-item-card:: ☎ How-To
      :link: how-to
      :link-type: ref

      Getting started.

   .. grid-item-card:: 📖 API reference
      :link: pyiso13786-api
      :link-type: ref

      The reference guide contains a detailed description of the ISO_13786 API.
      It describes how the methods work and which parameters can be used.

.. grid::

   .. grid-item-card:: 📚 Examples
      :link: examples
      :link-type: ref

      A gallery of examples ((tbd)).


.. admonition:: Highlights
   :class: admonition

   + 100 % Python package built with `NumPy <https://numpy.org/>`_

   + easy to learn and productive high-level :ref:`API <iso-13786-api>`


Installation
------------
Install Python, open a terminal, go to the directory of the cloned repository
and run

.. code-block:: shell

   pip install .


.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
   examples/index
   howto
   pyiso13786

License
-------

Legal / Intellectual Property
-----------------------------

This package implements calculation methods described in **ISO 13786** (“Thermal
performance of building components — Dynamic thermal characteristics — Calculation
methods”). The ISO standard document itself is copyrighted by ISO and must be obtained
from ISO or a national standards body.

This project:

- Is **not** an official ISO publication.
- Is **not** endorsed or approved by ISO.
- Does **not** include the text of the ISO standard.

The code and documentation in this repository are provided under the project’s open‑source
license (see `LICENSE`). Any use of this software is subject to that license and does not
grant any rights to reproduce or redistribute the ISO standard itself.

pyiso13786 - (C) 2026 Achim Geissler, Reinach BL (Switzerland).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see `<https://www.gnu.org/licenses/>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
