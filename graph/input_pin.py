class InputPin:
    """
    The Rosetta graph input pin
    """
    # TODO: Should be able to find connected output pin - so traversal up the graph is possible.
    def __init__(self, pin_name, mime_type_map, filter):
        """
        c'tor
        :param pin_name: The name of the pin for diagnostics, etc.
        :param mime_type_map: Maps a mime type to a handler. * maps everything.
        :param filter: A reference to the filter to which this pin belongs.
        """
        self._pin_name = pin_name
        self._mime_type_map = mime_type_map
        self._filter = filter

    @property
    def pin_name(self):
        return self._pin_name

    def recv(self, mime_type, payload, metadata_dict):
        """
        Receive a payload. Payload must be in either str or a binary sequence convertible to bytes format.

        :param mime_type: The mime_type of the payload being received
        :param payload: The payload to be received
        :param metadata_dict: A dictionary of metadata values to be passed down the filter chain
        :return: None
        """
        disp_fun = self._mime_type_map.get(mime_type)
        if disp_fun is None:
            disp_fun = self._mime_type_map.get('*')
            if disp_fun is None:
                raise ValueError("Pin {0} could not find a dispatcher for {1}".format(self._pin_name, mime_type))
        disp_fun(mime_type, payload, metadata_dict)

    # def recv_str(self, mime_type, payload, metadata_dict):
    #     """
    #     Receive a payload in Python string format
    #
    #     :param mime_type: The mime_type of the payload being received
    #     :param payload: The payload to be sent
    #     :param metadata_dict: A dictionary of metadata values to be passed down the filter chain
    #     :return: None
    #     """
    #     disp_fun = self._mime_type_map.get(mime_type)
    #     if disp_fun is None:
    #         disp_fun = self._mime_type_map.get('*')
    #         if disp_fun is None:
    #             raise ValueError("Pin {0} could not find a dispatcher for {1}".format(self._pin_name, mime_type))
    #     disp_fun(mime_type, payload, metadata_dict)
