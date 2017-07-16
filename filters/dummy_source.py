from graph.filter_base import FilterBase, FilterState
from graph.output_pin import OutputPin


class DummySource(FilterBase):
    """
    A dummy filter source
    TODO: Delete this one day soon
    """

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager)
        self._output_pin = OutputPin('output', True)
        self._add_output_pin(self._output_pin)

    def run(self):
        super().run()
        mtype = 'application/json'
        mdict = {}
        j1 = "{ 'test': 'value', 'test2': 123, 'test3': true }"
        j2 = "{ 'foo': 'bar', 'foo2': 456.789, 'foo3': false }"
        self._output_pin.send(mtype, j1, mdict)
        self._output_pin.send(mtype, j2, mdict)
        mtype2 = 'application/octet-stream'
        b1 = bytes([1, 2, 3, 4, 5])
        self._output_pin.send(mtype2, b1, mdict)
        self._set_filter_state(FilterState.running)

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)
