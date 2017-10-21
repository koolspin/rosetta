import argparse
from graph.graph_manager import GraphManager

parser = argparse.ArgumentParser()
parser.add_argument("filter_name")
args = parser.parse_args()
print('filter: {0}'.format(args.filter_name))

graph_manager = GraphManager()
meta_list = graph_manager.get_filter_metadata('filters.dummy_source', 'DummySource')
print('meta: {0}'.format(meta_list[0]))
for key, val in meta_list[1].items():
    print('pad: {0}'.format(key))
    print('type: {0}'.format(val.type))
    print('availability: {0}'.format(val.availability))
    for cap in val.capabilities:
        print('cap mime: {0}'.format(cap.mime_type))
        print('cap props: {0}'.format(cap.pad_properties))

