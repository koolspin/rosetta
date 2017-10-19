import argparse
from graph.graph_manager import GraphManager

parser = argparse.ArgumentParser()
parser.add_argument("filter_name")
args = parser.parse_args()
print('filter: {0}'.format(args.filter_name))

graph_manager = GraphManager()
meta_dict = graph_manager.get_filter_metadata('filters.dummy_source', 'DummySource')
print('meta: {0}'.format(meta_dict))

