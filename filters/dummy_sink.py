from graph.filter_base import FilterBase, FilterState, FilterType
from graph.input_pin import InputPin


class DummySink(FilterBase):
    """
    A dummy sink. Takes input and does absolutely nothing with it.

    Input Pins:
    input - Accepts any mime type.
    """
    filter_pad_templates = {}
    filter_meta = {}

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.sink)
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)

    def run(self):
        super().run()
        self._set_filter_state(FilterState.running)

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)

    def recv(self, mime_type, payload, metadata_dict):
        if self.filter_state == FilterState.running:
            self._cycle_ended()
        else:
            raise RuntimeError('{0} tried to process input while filter state is {1}'.format(self.filter_name, self.filter_state))

    @staticmethod
    def get_filter_metadata():
        return FilterBase.filter_meta

    @staticmethod
    def get_filter_pad_templates():
        return FilterBase.filter_pad_templates

