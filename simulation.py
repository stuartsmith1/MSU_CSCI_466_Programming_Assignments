from network import Router, Host
from link import Link, LinkLayer
import threading
from time import sleep
from rprint import print

# configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 10  # give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads at the end

    # create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)

    # create routers and routing tables for connected clients (subnets)
    encap_tbl_D = {0: 'B', 1: 'C'}  # table used to encapsulate network packets into MPLS frames
    frwd_tbl_D = {'B': ['A', 'H1', 2], 'C': ['A', 'RB', 3]}  # table used to forward MPLS frames
    decap_tbl_D = {'A': False, 'Z': False, 'B': True}  # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA',
                      intf_capacity_L=[500, 500, 500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_a)
    
    encap_tbl_D = {0: 'B', 1: 'C'}
    frwd_tbl_D = {'Z': ['A', 'H2', 1], 'A': ['A', 'RA', 1], 'B': ['A', 'RA', 1], 'C': ['A', 'RA', 1]}
    decap_tbl_D = {'A': False, 'Z': False, 'B': True}
    router_b = Router(name='RB',
                      intf_capacity_L=[500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_b)

    encap_tbl_D = {0: 'B', 1: 'C'}
    frwd_tbl_D = {'Z': ['A', 'H2', 1], 'A': ['A', 'RA', 1], 'B': ['A', 'RA', 1], 'C': ['A', 'RA', 1]}
    decap_tbl_D = {'A': False, 'Z': False, 'B': True}
    router_c = Router(name='RC',
                      intf_capacity_L=[500, 500],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_c)

    encap_tbl_D = {0: 'B', 1: 'C'}
    frwd_tbl_D = {'Z': ['A', 'H2', 1], 'A': ['Z', 'RA', 2], 'B': ['A', 'RA', 1], 'C': ['A', 'RA', 1]}
    decap_tbl_D = {'C': True, 'B': True, 'A': True, 'Z': True, 'H': False}
    router_d = Router(name='RD',
                      intf_capacity_L=[100, 100, 100],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    # add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(host_2, 0, router_a, 1))
    link_layer.add_link(Link(router_a, 2, router_b, 0))
    link_layer.add_link(Link(router_a, 3, router_c, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))
    link_layer.add_link(Link(router_c, 1, router_d, 1))
    link_layer.add_link(Link(router_d, 2, host_3, 0))
    
    # start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))
    
    for t in thread_L:
        t.start()

    # create some send events
    for i in range(1):
        priority = i % 2
        host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % i, priority)
    for i in range(1):
        priority = i % 2
        host_2.udt_send('H3', 'MESSAGE_%d_FROM_H2' % i, priority)
    
    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
    
    print("All simulation threads joined")