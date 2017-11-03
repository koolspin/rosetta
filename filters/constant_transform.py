from graph.filter_base import FilterBase, FilterState, FilterType
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class ConstantTransform(FilterBase):
    """
    A constant filter - injects constants into the metadata_dict.

    Input Pins:
    input - Accepts any mime type.

    Output Pins:
    output - Required - Whatever appears on input is copied to output with the metadata_dict modified according to the
                        configuration of this filter.
    """
    filter_pad_templates = {}
    filter_meta = {}
    CONFIG_KEY_MIME_TYPE = 'const_mime_type'
    CONFIG_KEY_PAYLOAD = 'const_payload'
    CONFIG_KEY_METADATA_DICT = 'const_metadata_dict'

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.transform)
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
        super().run()
        self._set_filter_state(FilterState.running)

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)

    def recv(self, mime_type, payload, metadata_dict):
        if self._metadata_dict is not None:
            for key in self._metadata_dict.keys():
                metadata_dict[key] = self._metadata_dict[key]
        if self.filter_state == FilterState.running:
            self._output_pin.send(self._mime_type, self._payload, metadata_dict)
        else:
            raise RuntimeError('{0} tried to process input while filter state is {1}'.format(self.filter_name, self.filter_state))

    @staticmethod
    def get_filter_metadata():
        return FilterBase.filter_meta

    @staticmethod
    def get_filter_pad_templates():
        return FilterBase.filter_pad_templates
