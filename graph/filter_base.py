from enum import Enum

from graph.pad import Pad


class FilterState(Enum):
    """
    This enum contains the various states a filter can be in.

    Run Flow:
    - Graph manager calls "run" on a filter
    - Filter transitions immediately to run_pending
    - When the filter completes the transition, it sets internal state to running and informs the graph manager via filter_state_changed
    - When the graph manager sees all filters have transitioned to running, it calls graph_is_running on each filter

    Stop Flow:
    - Graph manager calls "stop" on a filter
    - Filter transitions immediately to stop_pending
    - When the filter completes the transition, it sets internal state to stopped and informs the graph manager via filter_state_changed
    - From this point on, the filter has flushed all pending internal processing and can no longer generate output
    - When the graph manager sees all filters have transitioned to stopped, it calls graph_has_stopped on each filter
    """
    stopped = 0
    run_pending = 1
    running = 2
    stop_pending = 3
    # The filter has entered an unexpected error state - maybe delete and reallocate a new one
    error = 4


class FilterType(Enum):
    """
    This enum contains the types of filter.

    source: Filter is used to generate data to be passed down the pipline.
            Examples: File reader, HTTP get, web server, network socket, constants and literal values.

    transform: Filter is used to optionally change the format or content of the payload.
               Examples: Logger, XML -> JSON converter, Base64 encoder / decoder, Protocol buf serializer.

    sink: Filter is used to write or send data elsewhere.
          Examples: File writer, HTTP post, sqlite db, postgresql db, network socket, etc.

    A valid graph must contain at least one source and one sink.
    TODO: How do we handle filters that can be both like a network socket?
    """
    # TODO: Deprecated
    source = 1
    sink = 2
    source_sink = 3
    transform = 4


class FilterBase:
    """
    Rosetta graph filter base object
    """
    #### Filter ranks
    FILTER_RANK_NONE = 0
    FILTER_RANK_MARGINAL = 1
    FILTER_RANK_SECONDARY = 2
    FILTER_RANK_PRIMARY = 3

    #### Filter metadata
    # The name of the filter
    FILTER_META_NAME = 'FILTER_META_NAME'
    # Description
    FILTER_META_DESC = 'FILTER_META_DESC'
    # Version in major.minor.revision format
    FILTER_META_VER = 'FILTER_META_VER'
    # How likely this filter is to be automatically plugged into a graph (0-255)
    FILTER_META_RANK = 'FILTER_META_RANK'
    # Where did this thing come from?
    FILTER_META_ORIGIN_URL = 'FILTER_META_ORIGIN_URL'
    # Original author
    FILTER_META_AUTHOR = 'FILTER_META_AUTHOR'
    # Klass id - used for finding classes of filters. Ex: Source/DB, Sink/Network/Protocol/Device
    FILTER_META_KLASS = 'FILTER_META_KLASS'
    filter_meta = {}
    # Pad templates for this filter
    # Note this dictionary is keyed by the actual pad name and not the name template
    filter_pad_templates = {}

    def __init__(self, name, config_dict, graph_manager, filter_type):
        self._filter_name = name
        self._config_dict = config_dict
        self._source_pads = {}
        self._sink_pads = {}
        # Deprecated - remove
        self._input_pins = {}
        self._output_pins = {}
        self._filter_state = FilterState.stopped
        self._graph_manager = graph_manager
        self._filter_type = filter_type
        # This is the only protocol available now, might change in the future
        self._protocol_version = 1
        # A filter is continuous if it can generate multiple output events over a normal lifetime.
        # Ex: A web server filter or network socket filter
        # A filter is not continuous if it usually generates a single output event.
        # Ex: A file reader filter
        # A graph that contain no continuous filters is able to run in one-shot mode
        self._is_continuous = False
        # Make sure to crate the pads that are defined for this filter's template
        self._create_always_pads_from_template()

    @staticmethod
    def get_filter_metadata():
        return FilterBase.filter_meta

    @staticmethod
    def get_filter_pad_templates():
        return FilterBase.filter_pad_templates

    @property
    def protocol_version(self):
        return self._protocol_version

    @property
    def filter_name(self):
        return self._filter_name

    @property
    def filter_state(self):
        return self._filter_state

    @property
    def filter_type(self):
        return self._filter_type

    @property
    def is_continuous(self):
        return self._is_continuous

    def get_input_pin(self, input_pin_name):
        """
        Return a reference to the input pin by name
        :param input_pin_name: The name of the input pin to retrieve
        :return: An input pin reference or None if not found
        """
        ipin = self._input_pins.get(input_pin_name)
        return ipin

    def get_all_input_pins(self):
        return self._input_pins.items()

    def get_output_pin(self, output_pin_name):
        """
        Return a reference to the input pin by name
        :param output_pin_name: The name of the output pin to retrieve
        :return: An input pin reference or None if not found
        """
        opin = self._output_pins.get(output_pin_name)
        return opin

    def get_all_output_pins(self):
        return self._output_pins.items()

    def run(self):
        """
        Called by the graph manager (only) when the graph is transitioning to running
        :return:
        """
        if self._filter_state != FilterState.stopped and self._filter_state != FilterState.stop_pending:
            raise RuntimeError("Attempt to run a filter that is not in the stopped state")

    def graph_is_running(self):
        """
        Called by the graph manager (only) when the graph has transitioned to running
        :return:
        """
        pass

    def stop(self):
        """
        Called by the graph manager (only) when the graph is transitioning to stopping
        :return:
        """
        if self._filter_state != FilterState.running and self._filter_state != FilterState.run_pending:
            raise RuntimeError("Attempt to stop a filter that is not in the running state")

    def graph_has_stopped(self):
        """
        Called by the graph manager (only) when the graph has transitioned to stopped
        :return:
        """
        pass

    def _create_always_pads_from_template(self):
        """
        Create the always available pads from the templates defined for this filter
        :return: None
        """
        for key, val in FilterBase.filter_pad_templates.items():
            if val.is_present_always():
                new_pad = Pad.create_pad_from_template(val, key)
                if new_pad.is_src():
                    self._source_pads[key] = new_pad
                elif new_pad.is_sink():
                    self._sink_pads[key] = new_pad
                else:
                    raise Exception("Cannot add an unknown pad type from the source template")

    def _add_input_pin(self, input_pin):
        """
        Add an input pin to the collection
        :param input_pin: A reference to the input pin to be added
        :return: None
        """
        pin_name = input_pin.pin_name
        self._input_pins[pin_name] = input_pin

    def _add_output_pin(self, output_pin):
        """
        Add an output pin to the collection
        :param output_pin: A reference to the output pin to be added
        :return: None
        """
        pin_name = output_pin.pin_name
        self._output_pins[pin_name] = output_pin

    def _set_filter_state(self, new_state):
        """
        Set the filter to a new state and inform the graph manager
        :param new_state: The new state that we're transitioning to
        :return: None
        """
        self._filter_state = new_state
        self._graph_manager.filter_changed_state(self)

    def _cycle_started(self):
        """
        Called by source filters to mark the start of a cycle
        :return:
        """
        if self._filter_type == FilterType.source:
            self._graph_manager.cycle_started(self)
        else:
            raise RuntimeError("Could not start cycle because this is not a source filter - {0}".format(self.filter_name))

    def _cycle_ended(self):
        """
        Called by sink filters to mark the end of a cycle
        :return:
        """
        if self._filter_type == FilterType.sink:
            self._graph_manager.cycle_ended(self)
        else:
            raise RuntimeError("Could not end cycle because this is not a sink filter - {0}".format(self.filter_name))
