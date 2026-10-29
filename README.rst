Laser Risk Damage Calculator
############################

Vitrine d'une architecture ouverte pour la sécurité laser : un schéma de données public, un
cœur Python pur (sans interface graphique ni serveur) et des interfaces qui s'y branchent.
Le contexte et les décisions sont dans le document de cadrage du projet.

.. warning::
   Les calculs d'exposition sont **illustratifs** : un seul cas est implémenté (faisceau
   continu visible, 400 à 700 nm). Ils doivent être validés par des référents laser avant
   tout usage réel. Le schéma est en version 0.1.0 et va évoluer.

Installation
============

.. code-block:: bash

    pip install -e .            # cœur : pint et pydantic seulement
    pip install -e ".[qt]"      # interface autonome PyQt / PyMoDAQ
    pip install -e ".[test]"    # tests

Ce que montre la vitrine
========================

Un parc, des lasers, plusieurs faisceaux par laser
--------------------------------------------------

Les modèles sont des classes pydantic, les grandeurs physiques s'écrivent avec leur unité.

.. code-block:: python

    from laser_risk_calculator import Beam, Laser, LaserType

    laser = Laser(name='Ti:Sa femtoseconde', beams=[
        Beam(name='fondamental', laser_type=LaserType.Pulsed, wavelength='800 nm',
             power='1.5 W', pulse_duration='100 fs', repetition_rate='80 MHz'),
        Beam(name='harmonique-2', laser_type=LaserType.Pulsed, wavelength='400 nm',
             power='200 mW', pulse_duration='100 fs', repetition_rate='80 MHz'),
    ])

Un fichier JSON de référence et son schéma
------------------------------------------

``examples/parc_exemple.json`` est un parc complet. Le JSON Schema publié dans
``schema/laser_park.schema.json`` est tiré des modèles :

.. code-block:: bash

    python -m laser_risk_calculator schema > schema/laser_park.schema.json
    python -m laser_risk_calculator show examples/parc_exemple.json

.. code-block:: python

    from laser_risk_calculator.storage import load_park, save_park

    park = load_park('examples/parc_exemple.json')   # valide les références entre objets
    save_park(park, 'copie.json')

Un calcul séparé des interfaces
-------------------------------

.. code-block:: python

    from laser_risk_calculator.calculator.exposure import evaluate

    result = evaluate(park.laser('hene-01').beam('main'))
    print(result.mpe, result.nohd, result.source)   # 25.5 W/m², 12.6 m

.. code-block:: bash

    python -m laser_risk_calculator exposure examples/parc_exemple.json hene-01

Compatibilité eLabFTW (esquisse)
--------------------------------

Un laser correspond à une ressource eLabFTW dont les métadonnées contiennent le JSON du
laser. ``storage/elabftw.py`` ne fait aucun appel réseau et sa forme est à valider avec les
développeurs d'eLabFTW.

.. code-block:: python

    from laser_risk_calculator.storage.elabftw import laser_from_resource, laser_to_resource

    resource = laser_to_resource(park.laser('ti-sa-01'), category_id=7)
    assert laser_from_resource(resource) == park.laser('ti-sa-01')

Une interface autonome
----------------------

.. code-block:: bash

    laser-risk-gui      # nécessite l'option [qt]

L'interface ne contient aucune logique de calcul.

Structure
=========

::

    src/laser_risk_calculator/
        units.py            grandeurs avec unités (pint)
        calculator/         laser.py, park.py (schéma), exposure.py (calcul)
        storage/            json_file.py, elabftw.py
        schema.py, cli.py   JSON Schema et ligne de commande
        qt_backend/         interface autonome
    examples/, schema/, tests/
