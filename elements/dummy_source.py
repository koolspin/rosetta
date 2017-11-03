from graph.filter_base import FilterBase, FilterState, FilterType
from graph.pad_template import PadTemplate
from graph.pad_capabilities import PadCapabilities


def get_plugin_metadata():
    return ['DummySource']

class DummySource(FilterBase):
    """
    A dummy filter source. Useful for debugging, but should be replaced with a constant_source filter one day.
    TODO: Delete this one day soon
    """
    #########################################################################
    # Note - these static methods MUST be implemented by all filters.
    print('######## Executing static variable init on DummySource')
    filter_meta = {}
    filter_meta[FilterBase.FILTER_META_FULLY_QUALIFIED] = "com.urbtek.dummy_source"
    filter_meta[FilterBase.FILTER_META_NAME] = "DummySource"
    filter_meta[FilterBase.FILTER_META_DESC] = "A dummy source filter"
    filter_meta[FilterBase.FILTER_META_VER] = "0.9.0"
    filter_meta[FilterBase.FILTER_META_RANK] = FilterBase.FILTER_RANK_NONE
    filter_meta[FilterBase.FILTER_META_ORIGIN_URL] = "https://github.com/koolspin"
    filter_meta[FilterBase.FILTER_META_KLASS] = "Source/Dummy"

    # Pad templates for this filter
    # Note this dictionary is keyed by the actual pad name and not the name template
    filter_pad_templates = {}
    src_pad_cap = PadCapabilities.create_caps_any()
    src_pad_template = PadTemplate.create_pad_always_source([src_pad_cap])
    filter_pad_templates[FilterBase.DEFAULT_SOURCE_PAD_NAME] = src_pad_template
    # End of filter metadata
    #########################################################################

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.sink)
        # Make sure to crate the pads that are defined for this filter's template
        self._create_always_pads_from_template(DummySource.filter_pad_templates)
        self._source_pad = self.get_source_pad(FilterBase.DEFAULT_SOURCE_PAD_NAME)

    def run(self):
        super().run()
        mtype = 'application/json'
        mdict = {}
        j1 = "{ 'test': 'value', 'test2': 123, 'test3': true }"
        j2 = "{ 'foo': 'bar', 'foo2': 456.789, 'foo3': false }"
        self._source_pad.send(mtype, j1, mdict)
        self._source_pad.send(mtype, j2, mdict)
        mtype2 = 'application/octet-stream'
        b1 = bytes([1, 2, 3, 4, 5])
        self._source_pad.send(mtype2, b1, mdict)
        self._set_filter_state(FilterState.running)

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)

    #########################################################################
    # Note - these static methods MUST be implemented by all filters.
    # TODO: Is there a better way to do this?
    @staticmethod
    def get_filter_metadata():
        return DummySource.filter_meta

    @staticmethod
    def get_filter_pad_templates():
        return DummySource.filter_pad_templates

