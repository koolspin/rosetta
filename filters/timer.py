import asyncio
from contextlib import suppress
from graph.filter_base import FilterBase, FilterState, FilterType
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class Timer(FilterBase):
    """
    A timer filter to trigger a request at given intervals
    """
    # TODO: Make these constants generic
    filter_pad_templates = {}
    filter_meta = {}
    CONFIG_KEY_MIME_TYPE = 'timer_mime_type'
    CONFIG_KEY_PAYLOAD = 'timer_payload'
    CONFIG_KEY_METADATA_DICT = 'timer_metadata_dict'
    CONFIG_KEY_TIMER_DELAY_SECONDS = 'timer_delay_seconds'

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.source)
        self._is_continuous = True
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)
        self._output_pin = OutputPin('output', True)
        self._add_output_pin(self._output_pin)
        self._mime_type = config_dict[Timer.CONFIG_KEY_MIME_TYPE]
        self._payload = config_dict[Timer.CONFIG_KEY_PAYLOAD]
        self._metadata_dict = config_dict.get(Timer.CONFIG_KEY_METADATA_DICT)
        self._timer_delay_seconds = config_dict.get(Timer.CONFIG_KEY_TIMER_DELAY_SECONDS)
        if self._timer_delay_seconds is None:
            self._timer_delay_seconds = 5.0
        self._timer_task = None

    def run(self):
        super().run()
        self._set_filter_state(FilterState.running)

    def graph_is_running(self):
        super().graph_is_running()
        self._cycle_started()
        self._task = asyncio.ensure_future(self._run())

    def stop(self):
        super().stop()
        self._stop()
        self._set_filter_state(FilterState.stopped)

    def recv(self, mime_type, payload, metadata_dict):
        # TODO: What should we do here
        pass

    async def _run(self):
        while True:
            await asyncio.sleep(self._timer_delay_seconds)
            self._output_pin.send(self._mime_type, self._payload, self._metadata_dict)

    async def _stop(self):
        self._timer_task.cancel()
        with suppress(asyncio.CancelledError):
            await self._timer_task

    @staticmethod
    def get_filter_metadata():
        return FilterBase.filter_meta

    @staticmethod
    def get_filter_pad_templates():
        return FilterBase.filter_pad_templates
