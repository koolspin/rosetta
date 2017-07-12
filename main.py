from threading import Thread
import asyncio
from graph.graph_builder import GraphBuilder
from graph.graph_manager import GraphManager

with open('config.json', 'r') as myfile:
    config_txt = myfile.read()

graph_manager = GraphManager()
graph_builder = GraphBuilder(graph_manager, config_txt)
graph_builder.build_graph()

def start_loop(loop):
    asyncio.set_event_loop(loop)
    # Run the graph
    graph_manager.run()
    loop.run_forever()

new_loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(new_loop,))
t.start()

# Wait for termination
try:
    print("Waiting for termination...")
    t.join()
    print("...after join")
finally:
    print("...executing finally")
    # graph_manager.stop()
    new_loop.stop()
    print("all done!")
