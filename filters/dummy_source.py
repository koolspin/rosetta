from graph.filter_base import FilterBase, FilterState, FilterType
from graph.pad_template import PadTemplate
from graph.pad_capabilities import PadCapabilities
from graph.output_pin import OutputPin


class DummySource(FilterBase):
    """
    A dummy filter source. Useful for debugging, but should be replaced with a constant_source filter one day.
    TODO: Delete this one day soon
    """
    FilterBase.filter_meta[FilterBase.FILTER_META_NAME] = "DummySource"
    FilterBase.filter_meta[FilterBase.FILTER_META_DESC] = "A dummy source filter"
    FilterBase.filter_meta[FilterBase.FILTER_META_VER] = "0.9.0"
    FilterBase.filter_meta[FilterBase.FILTER_META_RANK] = FilterBase.FILTER_RANK_NONE
    FilterBase.filter_meta[FilterBase.FILTER_META_ORIGIN_URL] = "https://github.com/koolspin"
    FilterBase.filter_meta[FilterBase.FILTER_META_KLASS] = "Source/Dummy"

    # Create a source pad that creates anything and is always available
    src_pad_cap = PadCapabilities.create_caps_any()
    src_pad_template = PadTemplate.create_pad_always_source([src_pad_cap])
    FilterBase.filter_pad_templates['src'] = src_pad_template

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.sink)
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
