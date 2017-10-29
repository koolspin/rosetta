import argparse
from graph.graph_manager import GraphManager

parser = argparse.ArgumentParser()
parser.add_argument("filter_name")
args = parser.parse_args()
print('filter: {0}'.format(args.filter_name))

def print_meta(meta_list):
    print('meta: {0}'.format(meta_list[0]))
    for key, val in meta_list[1].items():
        print('pad: {0}-{1}'.format(key, val))
        caps = val.caps
        for cap in caps:
            print('cap: {0}'.format(cap))


graph_manager = GraphManager()
meta_list = graph_manager.get_filter_metadata('filters.dummy_source', 'DummySource')
meta_logger = graph_manager.get_filter_metadata('filters.logger_sink', 'LoggerSink')
print_meta(meta_list)
print_meta(meta_logger)

