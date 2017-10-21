from graph.filter_base import FilterBase, FilterState, FilterType, FilterPadTemplate, PadCapabilities
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

    # Our one and only source pad
    src_pad = FilterPadTemplate()
    src_pad.name = 'src'
    src_pad.type = FilterPadTemplate.PAD_TYPE_SOURCE
    src_pad.availability = FilterPadTemplate.AVAILABILITY_ALWAYS

    src_pad_cap = PadCapabilities()
    src_pad_cap.mime_type = 'application/octet-stream'
    src_pad_cap.pad_properties['format'] = ['foo', 'temp', 'boo']
    src_pad_cap.pad_properties['fizzbuzz'] = ['moo', 'cow']

    src_pad.capabilities.append(src_pad_cap)

    FilterBase.filter_pad_templates[src_pad.name] = src_pad

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.source)
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
