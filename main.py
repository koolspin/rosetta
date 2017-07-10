from graph.graph_builder import GraphBuilder
from graph.graph_manager import GraphManager

with open('config.json', 'r') as myfile:
    config_txt = myfile.read()

graph_manager = GraphManager()
graph_builder = GraphBuilder(graph_manager, config_txt)
graph_builder.build_graph()

# Run the graph
graph_manager.run()

