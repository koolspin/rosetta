import importlib


class GraphManager:
    """
    Manages the entire graph
    """
    def __init__(self):
        self._filters = {}

    @staticmethod
    def filter_factory(module_path, class_name, instance_name, config_dict):
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
        inst = klass(instance_name, config_dict)
        return inst

    def add_filter(self, filter):
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

    def run(self):
        """
        Run the graph by asking each filter to transition to run mode
        :return:
        """
        for key, val in self._filters.items():
            val.run()

    def stop(self):
        raise NotImplementedError("stop method must be implemented")
