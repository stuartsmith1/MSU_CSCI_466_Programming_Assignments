"""
Created on Oct 12, 2016

@author: mwittie
"""

import network
import link
import threading
from time import sleep
from rprint import print


# configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 8  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
	object_L = []  # keeps track of objects, so we can kill their threads
	routing_table = {0: 0, 1: 1}
	
	# create network nodes
	client1 = network.Host(1)
	client2 = network.Host(2)
	object_L.append(client1)
	object_L.append(client2)
	server3 = network.Host(3)
	server4 = network.Host(4)
	object_L.append(server3)
	object_L.append(server4)
	router_a = network.Router(routing_table, name='A', intf_count=2, max_queue_size=router_queue_size)
	object_L.append(router_a)
	router_b = network.Router(routing_table, name='B', intf_count=1, max_queue_size=router_queue_size)
	object_L.append(router_b)
	router_c = network.Router(routing_table, name='C', intf_count=1, max_queue_size=router_queue_size)
	object_L.append(router_c)
	router_d = network.Router(routing_table, name='D', intf_count=2, max_queue_size=router_queue_size)
	object_L.append(router_d)
	
	# create a Link Layer to keep track of links between network nodes
	link_layer = link.LinkLayer()
	object_L.append(link_layer)
	
	# add all the links
	# link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
	link_layer.add_link(link.Link(client1, 0, router_a, 0, 50))
	link_layer.add_link(link.Link(client2, 0, router_a, 1, 50))
	link_layer.add_link(link.Link(router_a, 0, router_b, 0, 50))
	link_layer.add_link(link.Link(router_a, 1, router_c, 0, 30))
	link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50))
	link_layer.add_link(link.Link(router_c, 0, router_d, 1, 50))
	link_layer.add_link(link.Link(router_d, 0, server3, 0, 30))
	link_layer.add_link(link.Link(router_d, 1, server4, 0, 50))
	
	# start all the objects
	thread_L = [threading.Thread(name=object.__str__(), target=object.run) for object in object_L]
	for t in thread_L:
		t.start()
	
	# create some send events
	#client1.udt_send(3, 'This is a string of data that is at least 80 characters long. Crazy!')
	client1.udt_send(3, 'This is a string of data for three.')
	client2.udt_send(4, 'This is a string of data for four.')


	
	# give the network sufficient time to transfer all packets before quitting
	sleep(simulation_time)
	
	# join all threads
	for o in object_L:
		o.stop = True
	for t in thread_L:
		t.join()
	
	print("All simulation threads joined")
