from graph.filter_base import FilterBase
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class ConstantFilter(FilterBase):
    """
    A constant filter
    """
    CONFIG_KEY_MIME_TYPE = 'const_mime_type'
    CONFIG_KEY_PAYLOAD = 'const_payload'
    CONFIG_KEY_METADATA_DICT = 'const_metadata_dict'

    def __init__(self, name, config_dict):
        super().__init__(name, config_dict)
        self._mime_type = config_dict[ConstantFilter.CONFIG_KEY_MIME_TYPE]
        self._payload = config_dict[ConstantFilter.CONFIG_KEY_PAYLOAD]
        self._metadata_dict = config_dict.get(ConstantFilter.CONFIG_KEY_METADATA_DICT)
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)
        self._output_pin = OutputPin('output', True)
        self._add_output_pin(self._output_pin)

    def run(self):
        pass

    def stop(self):
        pass

    def recv(self, mime_type, payload, metadata_dict):
        if self._metadata_dict is not None:
            for key in self._metadata_dict.keys():
                metadata_dict[key] = self._metadata_dict[key]
        self._output_pin.send(self._mime_type, self._payload, metadata_dict)
