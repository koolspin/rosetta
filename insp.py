import argparse

from filters.dummy_source import DummySource
from filters.logger_sink import LoggerSink
from graph.element_registry_manager import ElementRegistryManager
from graph.graph_manager import GraphManager


def print_meta(m_list):
    print('meta: {0}'.format(m_list[0]))
    for key, val in m_list[1].items():
        print('pad: {0}-{1}'.format(key, val))
        caps = val.caps
        for cap in caps:
            print('cap: {0}'.format(cap))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter_name")
    args = parser.parse_args()
    if args.filter_name is not None:
        print('filter: {0}'.format(args.filter_name))

    reg_manager = ElementRegistryManager()
    reg_manager.build_registry()
    reg_manager.dump_registry()

    graph_manager = GraphManager()
    meta_list = graph_manager.get_filter_metadata('filters.dummy_source', 'DummySource')
    meta_logger = graph_manager.get_filter_metadata('filters.logger_sink', 'LoggerSink')
    print_meta(meta_list)
    print_meta(meta_logger)

    dummy_source = DummySource('dummy', {}, graph_manager)
    logger_sink = LoggerSink('logger', {}, graph_manager)

