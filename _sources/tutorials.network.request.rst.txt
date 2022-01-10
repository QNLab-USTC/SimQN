Request management
========================

The request management module can select several sessions (a source node and destination node) randomly for large-scale evaluation. A ``Request`` includes the following attributions:

- ``src``: the source node
- ``dest``: the destination node
- ``attr``: the attributions of this session, such as the fidelity requirement, the QoS or the bandwidth requirement.

``QuantumNetwork`` provides ``add_request`` to manually add a new request and ``random_requests`` to randomly generate several requests:

.. code-block:: python

    # randomly generate 5 requests
    net.random_requests(number=5)

    # random generate 5 requests, but nodes can have multiple requests (allow overlay)
    net.random_requests(number=5, allow_overlay=True)

    # random generate 5 requests, with certain attributions
    net.random_requests(number=5, attr={"qos":2})

    # manually add a request
    net.add_request(Request(src=n1, dest=n3, attr={"qos":2}))

The network object and the nodes can query the related requests:

.. code-block:: python

    net.requests # get all requests

    n1.requests # get all requests related to n1
    
    n1.clear_request() # remote all requests on n1

Example applications and protocols
========================================

SimQN provides two example applications at ``qns.network.protocol``. ``BB84SendApp`` and ``BB84RecvApp`` is the simple demonstration protocol for BB84 QKD protocol without the after procedures, including error detecting, information reconciliation, and privacy amplification. ``EntanglementDistributionApp`` provides a hop-by-hop entanglement distribution protocol, where the source distribute entanglements to the destination at a fixed rate.

Those examples may be helpful for users to implement their own protocols. SimQN is working on providing more internal protocols for more scenarios.

