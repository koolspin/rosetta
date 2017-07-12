class FilterBase:
    """
    Rosetta graph filter base object
    """
    def __init__(self, name, config_dict):
        self._filter_name = name
        self._config_dict = config_dict
        self._input_pins = {}
        self._output_pins = {}

    @property
    def filter_name(self):
        return self._filter_name

    def get_input_pin(self, input_pin_name):
        """
        Return a reference to the input pin by name
        :param input_pin_name: The name of the input pin to retrieve
        :return: An input pin reference or None if not found
        """
        ipin = self._input_pins.get(input_pin_name)
        return ipin

    def get_output_pin(self, output_pin_name):
        """
        Return a reference to the input pin by name
        :param output_pin_name: The name of the output pin to retrieve
        :return: An input pin reference or None if not found
        """
        opin = self._output_pins.get(output_pin_name)
        return opin

    def run(self):
        raise NotImplementedError("run method must be implemented")

    def stop(self):
        raise NotImplementedError("stop method must be implemented")

    def _add_input_pin(self, input_pin):
        """
        Add an input pin to the collection
        :param input_pin: A reference to the input pin to be added
        :return: None
        """
        pin_name = input_pin.pin_name
        self._input_pins[pin_name] = input_pin

    def _add_output_pin(self, output_pin):
        """
        Add an output pin to the collection
        :param output_pin: A reference to the output pin to be added
        :return: None
        """
        pin_name = output_pin.pin_name
        self._output_pins[pin_name] = output_pin
