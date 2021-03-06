from graph.filter_base import FilterBase, FilterState, FilterType
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class TeeFilter(FilterBase):
    """
    T-Filter takes a single input and copies it to multiple outputs.
    The names of output filters will be 'output1' - 'outputn'
    """
    filter_pad_templates = {}
    filter_meta = {}
    CONFIG_KEY_OUTPUT_COUNT = 'output_pin_count'
    MAX_OUTPUT_COUNT = 128

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.transform)
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        input_pin = InputPin('input', mime_type_map, self)
        self._add_input_pin(input_pin)
        # config
        num_output = self._config_dict.get(TeeFilter.CONFIG_KEY_OUTPUT_COUNT)
        if num_output is None:
            # Default to 2 outputs - the simplest T-filter
            num_output = 2
        self._int_num_output = int(num_output)
        if self._int_num_output < 1 or self._int_num_output > TeeFilter.MAX_OUTPUT_COUNT:
            raise ValueError('{0} config item must be in the range of 1 to {1}'.format(TeeFilter.CONFIG_KEY_OUTPUT_COUNT, TeeFilter.MAX_OUTPUT_COUNT))
        #
        for i in range(self._int_num_output):
            output_pin_name = 'output{0}'.format(i+1)
            output_pin = OutputPin(output_pin_name, True)
            self._add_output_pin(output_pin)

    def run(self):
        super().run()
        self._set_filter_state(FilterState.running)

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)

    def recv(self, mime_type, payload, metadata_dict):
        if self.filter_state == FilterState.running:
            for output_pin in self._output_pins.values():
                output_pin.send(mime_type, payload, metadata_dict)
        else:
            raise RuntimeError('{0} tried to process input while filter state is {1}'.format(self.filter_name, self.filter_state))

    @staticmethod
    def get_filter_metadata():
        return FilterBase.filter_meta

    @staticmethod
    def get_filter_pad_templates():
        return FilterBase.filter_pad_templates
