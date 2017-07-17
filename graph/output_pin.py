class OutputPin:
    """
    The Rosetta graph output pin
    """
    def __init__(self, pin_name, required):
        """
        c'tor
        :param pin_name: The name of the pin for diagnostics, etc.
        :param required: Set True if it is required for this pin to be connected when the graph is started.
        """
        self._pin_name = pin_name
        self._required = required
        self._mime_types = []
        self._input_pin = None

    @property
    def pin_name(self):
        return self._pin_name

    @property
    def is_required(self):
        return self._required

    @property
    def is_connected(self):
        return self._input_pin is not None

    def connect_to_pin(self, input_pin):
        self._input_pin = input_pin

    def send(self, mime_type, payload, metadata_dict):
        """
        Send a payload. Payload must be in either str or a binary sequence convertible to bytes format.

        :param mime_type: The mime_type of the payload to be sent
        :param payload: The payload to be sent
        :param metadata_dict: A dictionary of metadata values to be passed down the filter chain
        :return: None
        """
        if self._required and (self._input_pin is None):
            raise ValueError("Output pin {0} is required, but not connected".format(self._pin_name))
        if self._input_pin is not None:
            self._input_pin.recv(mime_type, payload, metadata_dict)

