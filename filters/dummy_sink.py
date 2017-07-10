from graph.filter_base import FilterBase
from graph.input_pin import InputPin


class DummySink(FilterBase):
    """
    A dummy sink
    """

    def __init__(self, name, config_dict):
        super().__init__(name, config_dict)
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)

    def run(self):
        pass

    def recv(self, mime_type, payload, metadata_dict):
        pass

