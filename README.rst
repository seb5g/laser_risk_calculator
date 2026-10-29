Laser Risk Damage Calculator
############################

Showcase of an open architecture for laser safety: a public data schema, a pure Python core
(no graphical interface, no server) and interfaces that plug into it. The context and the
decisions are in the project scoping document.

.. warning::
   The exposure calculations are **illustrative**: a single case is implemented (continuous
   visible beam, 400 to 700 nm). They must be validated by laser safety officers before any
   real use. The schema is at version 0.1.0 and will evolve.

License
=======

The code is published under the EUPL-1.2 license (see ``LICENSE``). The data schema and its
documentation are planned under CC-BY 4.0. Versions of the code before this change were under
the MIT license; the author holds the rights.

Installation
============

.. code-block:: bash

    pip install -e .            # core: pint and pydantic only
    pip install -e ".[qt]"      # standalone PyQt / PyMoDAQ interface
    pip install -e ".[test]"    # tests

What the showcase demonstrates
==============================

A park, lasers, several beams per laser
---------------------------------------

The models are pydantic classes, and physical quantities are written with their unit.

.. code-block:: python

    from laser_risk_calculator import Beam, Laser, LaserType

    laser = Laser(name='Femtosecond Ti:Sa', beams=[
        Beam(name='fundamental', laser_type=LaserType.Pulsed, wavelength='800 nm',
             power='1.5 W', pulse_duration='100 fs', repetition_rate='80 MHz'),
        Beam(name='second-harmonic', laser_type=LaserType.Pulsed, wavelength='400 nm',
             power='200 mW', pulse_duration='100 fs', repetition_rate='80 MHz'),
    ])

A reference JSON file and its schema
------------------------------------

``examples/example_park.json`` is a complete park. The JSON Schema published in
``schema/laser_park.schema.json`` is generated from the models:

.. code-block:: bash

    python -m laser_risk_calculator schema > schema/laser_park.schema.json
    python -m laser_risk_calculator show examples/example_park.json

.. code-block:: python

    from laser_risk_calculator.storage import load_park, save_park

    park = load_park('examples/example_park.json')   # validates references between objects
    save_park(park, 'copy.json')

Collective protections
----------------------

Enclosures, door interlocks, beam stops, warning lights: each protection in place has a type,
a place, the lasers it protects, an optional interlock and the date of its last check. Risk
assessments refer to them by identifier.

.. code-block:: python

    for item in park.collective_protections:
        print(item.kind.value, item.laser_ids, item.interlocked)

A calculation separated from the interfaces
-------------------------------------------

.. code-block:: python

    from laser_risk_calculator.calculator.exposure import evaluate

    result = evaluate(park.laser('hene-01').beam('main'))
    print(result.mpe, result.nohd, result.source)   # 25.5 W/m², 12.6 m

.. code-block:: bash

    python -m laser_risk_calculator exposure examples/example_park.json hene-01

eLabFTW compatibility (sketch)
------------------------------

A laser maps to an eLabFTW resource whose metadata contains the laser JSON.
``storage/elabftw.py`` makes no network call and its shape is to be validated with the eLabFTW
developers.

.. code-block:: python

    from laser_risk_calculator.storage.elabftw import laser_from_resource, laser_to_resource

    resource = laser_to_resource(park.laser('ti-sa-01'), category_id=7)
    assert laser_from_resource(resource) == park.laser('ti-sa-01')

A standalone interface
----------------------

.. code-block:: bash

    laser-risk-gui      # requires the [qt] extra

The interface contains no calculation logic.

Layout
======

::

    src/laser_risk_calculator/
        units.py            quantities with units (pint)
        calculator/         laser.py, park.py (schema, protections), exposure.py (calculation)
        storage/            json_file.py, elabftw.py
        schema.py, cli.py   JSON Schema and command line
        qt_backend/         standalone interface
    examples/, schema/, tests/
