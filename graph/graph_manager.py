import importlib

from graph.filter_base import FilterState, FilterType


class GraphManager:
    """
    Manages the entire graph
    """
    def __init__(self):
        # All filters are mapped here
        self._filters = {}
        # FilterType specific mappings are here
        self._source_filters = {}
        self._transform_filters = {}
        self._sink_filters = {}
        # Set true if the graph is continuous - in other words, at least one filter is continuous
        self._is_continuous = False

    def filter_factory(self, module_path, class_name, instance_name, config_dict):
        """
        Create an instance of the specified filter
        :param module_path: The path to the module, for example filters.print_logger
        :param class_name: The name of the class
        :param instance_name: The name of the instance to be created
        :param config_dict: A dictionary used to configure the filter
        :return: Returns an instance of the class
        """
        mod = importlib.import_module(module_path)
        klass = getattr(mod, class_name)
        inst = klass(instance_name, config_dict, self)
        return inst

    def add_filter(self, filter):
        if filter.filter_name in self._filters:
            raise KeyError('A filter named {0} already exists in the graph'.format(filter.filter_name))
        self._filters[filter.filter_name] = filter

    def connect_pins(self, source_filter, source_pin, target_filter, target_pin):
        """
        Connnect an output pin (source_filter, source_pin) to an input pin (target_filter, target_pin)
        :param source_filter: The source filter to connect
        :param source_pin: The source (output) pin
        :param target_filter: The target filter to connect to
        :param target_pin: The target (input) pin
        :return:
        """
        sfilt = self._filters.get(source_filter)
        spin = sfilt.get_output_pin(source_pin)
        tfilt = self._filters.get(target_filter)
        tpin = tfilt.get_input_pin(target_pin)
        spin.connect_to_pin(tpin)

    def validate_graph(self):
        """
        Validate the graph as being valid.
        Here are the checks that are done:
        1. All filters that are part of the graph have the required pins connected.
        2. Every filter must have at least a single pin
        3. Must be at least one source filter in the graph
        4. Must be at least one sink filter in the graph
        :return: True if the graph is OK, False otherwise
        """
        validate_flag = True
        opin_count = 0
        ipin_count = 0
        for key, val in self._filters.items():
            print('Validating filter {0}'.format(val.filter_name))
            if val.is_continuous:
                self._is_continuous = True
            opins = val.get_all_output_pins()
            opin_count = len(opins)
            for opin_key, open_val in opins:
                if open_val.is_required:
                    if not open_val.is_connected:
                        print('Output pin {0} is required, but is not connected'.format(open_val.pin_name))
                        validate_flag = False
            ipins = val.get_all_input_pins()
            ipin_count = len(ipins)
            #
            if val.filter_type == FilterType.source:
                self._source_filters[val.filter_name] = val
            elif val.filter_type == FilterType.transform:
                self._transform_filters[val.filter_name] = val
            if val.filter_type == FilterType.sink:
                self._sink_filters[val.filter_name] = val
            else:
                print("Incorrect filter type for {0}".format(val.filter_name))
                validate_flag = False
        if ipin_count + opin_count < 1:
            print('Filter has no input or output pins')
            validate_flag = False
        if self._is_continuous:
            print('Filter graph is continuous')
        #
        print("{0} total filters in graph".format(len(self._filters)))
        print("{0} source filters in graph".format(len(self._source_filters)))
        print("{0} transform filters in graph".format(len(self._transform_filters)))
        print("{0} sink filters in graph".format(len(self._sink_filters)))
        if len(self._source_filters) < 1:
            print('Graph has no source filters')
            validate_flag = False
        if len(self._sink_filters) < 1:
            print('Graph has no sink filters')
            validate_flag = False
        return validate_flag

    def run(self):
        """
        Run the graph by asking each filter to transition to run mode
        :return:
        """
        for key, val in self._filters.items():
            val.run()

    def stop(self):
        for key, val in self._filters.items():
            val.stop()

    def filter_changed_state(self, filter):
        """
        Called by a filter when it has changed state
        :return:
        """
        print('Filter {0} has transitioned to {1}'.format(filter.filter_name, filter.filter_state))
        if filter.filter_state == FilterState.running:
            all_are_running = self._have_all_filters_transitioned(FilterState.running)
            if all_are_running:
                print('All filters have transitioned to running state. Sending graph_is_running event')
                for key, val in self._filters.items():
                    val.graph_is_running()
        elif filter.filter_state == FilterState.stopped:
            all_are_stopped = self._have_all_filters_transitioned(FilterState.stopped)
            if all_are_stopped:
                print('All filters have transitioned to stopped state. Sending graph_has_stopped event')
                for key, val in self._filters.items():
                    val.graph_has_stopped()

    def cycle_started(self, filter):
        """
        Called by a filter when a graph cycle has started (ie web request is made, file is read, etc)
        :param filter: A reference to the filter which is starting the cycle.
        :return:
        """
        print('cycle started - filter {0}'.format(filter.filter_name))

    def cycle_ended(self, filter):
        """
        Called by a filter when a graph cycle has ended (ie db is written, web response sent, etc)
        Note the cycle isn't actually ended until all sink filters in the current graph have reported the cycle ending.
        :param filter: A reference to the filter which is ending the cycle.
        :return:
        """
        print('cycle ended - filter {0}'.format(filter.filter_name))


    def _have_all_filters_transitioned(self, new_state):
        """
        Check if all filters have transitioned to the given state code
        :param new_state:
        :return: True if all filters have transitioned, false if not
        """
        all_transitioned = True
        for key, val in self._filters.items():
            if val.filter_state != new_state:
                all_transitioned = False
                break
        return all_transitioned

