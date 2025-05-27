#!/usr/bin/env python3
import sys
import copy
import math

INF = math.inf

class Router:
    def __init__(self, name):
        self._name = name
        self.distance_table = {}
        self.updates_to_process = []
        self.routing_table = {}
        self.update_neighbors = False

    def initialize_distance_table(self, nodes):
        nodes = sorted([n for n in nodes if n != self._name])
        for node in nodes:
            self.distance_table[node] = {n: INF for n in nodes}

    def print_distance_table(self):
        nodes = sorted(self.distance_table.keys())
        header = [' '] + nodes
        print('\t'.join(header))
        for dest in nodes:
            row = [dest] + [str(self.distance_table[dest][via]).replace('inf', 'INF') for via in nodes]
            print('\t'.join(row))

    def update_self(self, graph, routers_list):
        neighbors = graph.get_neighbors(self._name)
        for neighbor in neighbors:
            self.distance_table[neighbor][neighbor] = graph.adj_list[self._name][neighbor]
        for router in routers_list:
            if router._name not in neighbors and router._name != self._name:
                for dest in self.distance_table:
                    self.distance_table[dest][router._name] = INF
        self.update_neighbors = True

    def send_updates(self, neighbors, routers_list):
        if self.update_neighbors:
            for router in routers_list:
                if router._name in neighbors:
                    router.updates_to_process.append((self._name, copy.deepcopy(self.distance_table)))
            self.update_neighbors = False

    def process_received_tables(self):
        for received_from, received_distance_table in self.updates_to_process:
            for dest in self.distance_table:
                if dest == received_from:
                    continue
                for via_node in self.distance_table[dest]:
                    if via_node == received_from:
                        prev_cost = self.distance_table[dest][via_node]
                        cost_to_received = self.distance_table[received_from][received_from]
                        total_cost = cost_to_received + self.find_min_cost(received_distance_table, dest)[0]
                        self.distance_table[dest][received_from] = total_cost
                        if prev_cost != total_cost:
                            self.update_neighbors = True
        self.updates_to_process = []

    def create_routing_table(self):
        for dest in self.distance_table:
            min_cost, next_hop = self.find_min_cost(self.distance_table, dest)
            self.routing_table[dest] = (next_hop, min_cost)

    def find_min_cost(self, distance_table, dest):
        min_cost, next_hop = INF, None
        for node, cost in distance_table[dest].items():
            if cost < min_cost:
                min_cost, next_hop = cost, node
        return min_cost, next_hop

    def print_routing_table(self):
        self.create_routing_table()
        print(f"Routing Table of router {self._name}:")
        for dest in sorted(self.routing_table):
            print(f"{dest},{self.routing_table[dest][0]},{self.routing_table[dest][1]}")
        print()

    def process_after_update(self, graph, routers_list):
        original_distance_table = copy.deepcopy(self.distance_table)
        self.updates_to_process = []
        self.update_self(graph, routers_list)
        neighbors = graph.get_neighbors(self._name)
        for router in routers_list:
            if router._name in neighbors:
                for dest in router.routing_table:
                    if dest == self._name:
                        continue
                    cost_to_via = self.distance_table[router._name][router._name]
                    via_to_dest = router.routing_table[dest][1]
                    self.distance_table[dest][router._name] = cost_to_via + via_to_dest
        if self.distance_table != original_distance_table:
            self.update_neighbors = True

class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_edge(self, node1, node2, weight):
        for n1, n2 in [(node1, node2), (node2, node1)]:
            if n1 not in self.adj_list:
                self.adj_list[n1] = {}
            self.adj_list[n1][n2] = weight

    def remove_edge(self, node1, node2):
        for n1, n2 in [(node1, node2), (node2, node1)]:
            self.adj_list.get(n1, {}).pop(n2, None)

    def get_neighbors(self, node):
        return self.adj_list.get(node, {}).keys()

nodes_list = []
graph = Graph()

# Read in nodes
while (line := sys.stdin.readline().strip()) != "START":
    nodes_list.append(line)
    graph.adj_list[line] = {}

# Read in edges
while (line := sys.stdin.readline().strip()) != "UPDATE":
    node1, node2, weight = line.split()
    graph.add_edge(node1, node2, int(weight))

routers_list = []
for node in nodes_list:
    router = Router(node)
    router.initialize_distance_table(nodes_list)
    router.update_self(graph, routers_list)
    routers_list.append(router)

# Print initial tables at t=0
for router in sorted(routers_list, key=lambda x: x._name):
    print(f"Distance Table of router {router._name} at t=0")
    router.print_distance_table()
    print()

t = 1
previous_distance_table = {router._name: copy.deepcopy(router.distance_table) for router in routers_list}
while True:
    # Phase 1: Send updates
    for router in routers_list:
        router.send_updates(graph.get_neighbors(router._name), routers_list)
    
    # Phase 2: Process received tables
    for router in routers_list:
        router.process_received_tables()
    
    # Check convergence
    if all(router.distance_table == previous_distance_table[router._name] for router in routers_list):
        break
    
    # Print tables for current t
    for router in sorted(routers_list, key=lambda x: x._name):
        print(f"Distance Table of router {router._name} at t={t}")
        router.print_distance_table()
        print()
    
    # Update previous tables and increment t
    previous_distance_table = {router._name: copy.deepcopy(router.distance_table) for router in routers_list}
    t += 1
    
    # Early exit if no updates needed
    if all(not router.update_neighbors for router in routers_list):
        break

# Final routing tables
for router in sorted(routers_list, key=lambda x: x._name):
    router.print_routing_table()

# Handle topology updates
while True:
    line = sys.stdin.readline().strip()
    if line == "END":
        break
    node1, node2, weight = line.split()
    if int(weight) == -1:
        graph.remove_edge(node1, node2)
    else:
        graph.add_edge(node1, node2, int(weight))

# Process updates and reconverge
previous_distance_table = {router._name: copy.deepcopy(router.distance_table) for router in routers_list}
for router in routers_list:
    router.process_after_update(graph, routers_list)

if not all(router.distance_table == previous_distance_table[router._name] for router in routers_list):
    # Print updated tables
    for router in sorted(routers_list, key=lambda x: x._name):
        print(f"Distance Table of router {router._name} at t={t}")
        router.print_distance_table()
        print()
    t += 1

    # Second convergence phase
    while True:
        for router in routers_list:
            router.send_updates(graph.get_neighbors(router._name), routers_list)
        for router in routers_list:
            router.process_received_tables()
        
        if all(router.distance_table == previous_distance_table[router._name] for router in routers_list):
            break
        
        for router in sorted(routers_list, key=lambda x: x._name):
            print(f"Distance Table of router {router._name} at t={t}")
            router.print_distance_table()
            print()
        
        previous_distance_table = {router._name: copy.deepcopy(router.distance_table) for router in routers_list}
        t += 1
        
        if all(not router.update_neighbors for router in routers_list):
            break

    # Final routing tables after update
    for router in sorted(routers_list, key=lambda x: x._name):
        router.print_routing_table()
