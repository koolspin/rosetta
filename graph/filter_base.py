from enum import Enum


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


class FilterBase:
    """
    Rosetta graph filter base object
    """
    def __init__(self, name, config_dict, graph_manager):
        self._filter_name = name
        self._config_dict = config_dict
        self._input_pins = {}
        self._output_pins = {}
        self._filter_state = FilterState.stopped
        self._graph_manager = graph_manager

    @property
    def filter_name(self):
        return self._filter_name

    @property
    def filter_state(self):
        return self._filter_state

    def get_input_pin(self, input_pin_name):
        """
        Return a reference to the input pin by name
        :param input_pin_name: The name of the input pin to retrieve
        :return: An input pin reference or None if not found
        """
        ipin = self._input_pins.get(input_pin_name)
        return ipin

    def get_output_pin(self, output_pin_name):
        """
        Return a reference to the input pin by name
        :param output_pin_name: The name of the output pin to retrieve
        :return: An input pin reference or None if not found
        """
        opin = self._output_pins.get(output_pin_name)
        return opin

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
