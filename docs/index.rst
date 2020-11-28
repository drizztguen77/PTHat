Pulse Train Hat Python API Documentation
========================================

Introduction
============
This API contains classes for the Pulse Train Hat module sold by CNC Design Ltd.

This contains :class:'PTHat' class. This class provides all the primary functionality for the serial command interface
as well as all general commands. It basically builds the commands and sends them to the serial port as specified in
the command interface at http://pthat.com/index.php/command-set/

It includes the ability to run both instant and buffered commands. All commands currently existing for the PTHat
are included in the API.

It also contains supporting classes for :class:'Axis', :class:'ADC', :class:'AUX' and :class:'PWM' commands. Each of
the supporting classes extend the PTHat class.


Guide
-----

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   help
   api
   faq
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
