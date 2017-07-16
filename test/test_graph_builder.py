from filters.dummy_sink import DummySink
from filters.dummy_source import DummySource
from filters.print_logger import PrintLogger


class TestGraphBuilder:
    """
    A fake graph builder used only for testing
    """
    def __init__(self):
        self._filters = {}
        source_filter = DummySource('dummy_source')
        logging_filter = PrintLogger('print_logger')
        sink_filter = DummySink('dummy_sink')
        self._filters[source_filter.filter_name] = source_filter
        self._filters[logging_filter.filter_name] = logging_filter
        self._filters[sink_filter.filter_name] = sink_filter
        self._wire_up_pins()
        self._run_graph()

    def _wire_up_pins(self):
        src_filter = self._filters.get('dummy_source')
        src_output = src_filter.get_output_pin('output')
        logging_filter = self._filters.get('print_logger')
        logger_input = logging_filter.get_input_pin('input')
        logger_output = logging_filter.get_output_pin('output')
        sink_filter = self._filters.get('dummy_sink')
        sink_input = sink_filter.get_input_pin('input')
        # Connect pins
        src_output.connect_to_pin(logger_input)
        logger_output.connect_to_pin(sink_input)

    def _run_graph(self):
        for key, val in self._filters.items():
            val.run()
