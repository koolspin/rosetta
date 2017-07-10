import json


class GraphBuilder:
    """
    When passed a json config, build the graph accordingly.
    """
    def __init__(self, graph_mgr, config_text):
        self._graph_mgr = graph_mgr
        self._config_text = config_text

    def build_graph(self):
        """
        Build the graph with the previously stored config file.
        :return:
        """
        js_obj = json.loads(self._config_text)
        filter_array = js_obj.get('filters')
        for filt in filter_array:
            module_path = filt['module_path']
            class_name = filt['class_name']
            instance_name = filt['instance_name']
            config = filt['config']
            filter_instance = self._graph_mgr.filter_factory(module_path, class_name, instance_name, config)
            self._graph_mgr.add_filter(filter_instance)
        conn_array = js_obj.get('pin_connections')
        for conn in conn_array:
            source_filter = conn['source_filter']
            source_pin = conn['source_pin']
            target_filter = conn['target_filter']
            target_pin = conn['target_pin']
            self._graph_mgr.connect_pins(source_filter, source_pin, target_filter, target_pin)
