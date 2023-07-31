Installation
************

.. code-block:: bash

    pip install deeplogs

.. code-block:: python

    import deeplogs as dpl

    logger = dpl.Logger("v1")
    bar = dpl.Bar(logger)
    reader = dpl.Reader()