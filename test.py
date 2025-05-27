#!/usr/bin/env python3
import sys
import copy
import math

INFINITY = math.inf

class Node:
    def __init__(self, name):
        self.name = name
        self.cost_table = {}
        self.pending_updates = []
        self.routing_info = {}
        self.needs_update = False

    def setup_cost_table(self, all_nodes):
        nodes = list(all_nodes)
        if self.name in nodes:
            nodes.remove(self.name)
        for dest in nodes:
            self.cost_table[dest] = {}
            for via in nodes:
                self.cost_table[dest][via] = INFINITY

    def display_cost_table(self):
        destinations = sorted(self.cost_table.keys())
        header = [' '] + destinations
        print('\t'.join(header))
        for dest in destinations:
            row = [dest] + [str(self.cost_table[dest][via]).replace('inf', 'INF') for via in destinations]
            print('\t'.join(row))

    def refresh_costs(self, network, nodes):
        neighbors = network.neighbors(self.name)
        for neighbor in neighbors:
            self.cost_table[neighbor][neighbor] = network.edges[self.name][neighbor]
        for node in nodes:
            if node.name not in neighbors and node.name != self.name:
                for dest in self.cost_table:
                    self.cost_table[dest][node.name] = INFINITY
        self.needs_update = True

    def propagate_updates(self, neighbors, nodes):
        if self.needs_update:
            for node in nodes:
                if node.name in neighbors:
                    node.pending_updates.append((self.name, copy.deepcopy(self.cost_table)))
        self.needs_update = False

    def process_updates(self):
        for sender, received_table in self.pending_updates:
            for dest in self.cost_table:
                if dest == sender:
                    continue
                for via in self.cost_table[dest]:
                    if via == sender:
                        prev_cost = self.cost_table[dest][via]
                        cost_to_sender = self.cost_table[sender][sender]
                        alt_cost = cost_to_sender + self.min_cost(received_table, dest)[0]
                        self.cost_table[dest][sender] = alt_cost
                        if prev_cost != alt_cost:
                            self.needs_update = True
        self.pending_updates = []

    def min_cost(self, table, dest):
        min_c = INFINITY
        next_hop = None
        for via in table[dest]:
            if table[dest][via] < min_c:
                min_c = table[dest][via]
                next_hop = via
        return (min_c, next_hop)

    def build_routing_info(self):
        for dest in self.cost_table:
            min_c, next_hop = self.min_cost(self.cost_table, dest)
            self.routing_info[dest] = (next_hop, min_c)

    def display_routing_info(self):
        self.build_routing_info()
        print(f"Routing table of router {self.name}:")
        for dest in sorted(self.routing_info):
            print(f"{dest},{self.routing_info[dest][0]},{self.routing_info[dest][1]}")
        print()

    def update_after_topology_change(self, network, nodes):
        prev_table = copy.deepcopy(self.cost_table)
        self.pending_updates = []
        self.refresh_costs(network, nodes)
        neighbors = network.neighbors(self.name)
        for node in nodes:
            if node.name in neighbors:
                for dest in node.routing_info:
                    if dest == self.name:
                        continue
                    cost_to_neighbor = self.cost_table[node.name][node.name]
                    neighbor_to_dest = node.routing_info[dest][1]
                    self.cost_table[dest][node.name] = cost_to_neighbor + neighbor_to_dest
        if self.cost_table != prev_table:
            self.needs_update = True

class Network:
    def __init__(self):
        self.edges = {}

    def add_link(self, n1, n2, cost):
        for n in [n1, n2]:
            if n not in self.edges:
                self.edges[n] = {}
        self.edges[n1][n2] = cost
        self.edges[n2][n1] = cost

    def remove_link(self, n1, n2):
        if n1 in self.edges and n2 in self.edges[n1]:
            del self.edges[n1][n2]
        if n2 in self.edges and n1 in self.edges[n2]:
            del self.edges[n2][n1]

    def neighbors(self, node):
        return self.edges.get(node, {})

# Read node names
node_names = []
network = Network()
line = sys.stdin.readline().strip()
while line != "START":
    node_names.append(line)
    network.edges[line] = {}
    line = sys.stdin.readline().strip()

# Read edges
line = sys.stdin.readline().strip()
while line != "UPDATE":
    n1, n2, w = line.split()
    network.add_link(n1, n2, int(w))
    line = sys.stdin.readline().strip()

# Initialize nodes
nodes = []
for name in node_names:
    node = Node(name)
    node.setup_cost_table(node_names)
    node.refresh_costs(network, nodes)
    nodes.append(node)

# Print initial cost tables
for node in nodes:
    print(f"Distance Table of router {node.name} at t=0")
    node.display_cost_table()
    print()

# Run algorithm until convergence
t = 1
prev_tables = {node.name: copy.deepcopy(node.cost_table) for node in nodes}
while True:
    for node in nodes:
        node.propagate_updates(network.neighbors(node.name), nodes)
    for node in nodes:
        node.process_updates()
    if all(node.cost_table == prev_tables[node.name] for node in nodes):
        break
    prev_tables = {node.name: copy.deepcopy(node.cost_table) for node in nodes}
    for node in nodes:
        print(f"Distance Table of router {node.name} at t={t}")
        node.display_cost_table()
        print()
    t += 1
    if all(not node.needs_update for node in nodes):
        break

# Print routing tables
for node in nodes:
    node.display_routing_info()

# Process topology changes
while True:
    line = sys.stdin.readline().strip()
    if line == "END":
        break
    n1, n2, w = line.split()
    if int(w) == -1:
        network.remove_link(n1, n2)
    else:
        network.add_link(n1, n2, int(w))

# Store previous tables
prev_tables = {node.name: copy.deepcopy(node.cost_table) for node in nodes}
for node in nodes:
    node.update_after_topology_change(network, nodes)

# If no changes, exit
if all(node.cost_table == prev_tables[node.name] for node in nodes):
    sys.exit()

# Print updated cost tables
for node in nodes:
    print(f"Distance Table of router {node.name} at t={t}")
    node.display_cost_table()
    print()
t += 1

prev_tables = {node.name: copy.deepcopy(node.cost_table) for node in nodes}
while True:
    for node in nodes:
        node.propagate_updates(network.neighbors(node.name), nodes)
    for node in nodes:
        node.process_updates()
    if all(node.cost_table == prev_tables[node.name] for node in nodes):
        break
    prev_tables = {node.name: copy.deepcopy(node.cost_table) for node in nodes}
    for node in nodes:
        print(f"Distance Table of router {node.name} at t={t}")
        node.display_cost_table()
        print()
    t += 1
    if all(not node.needs_update for node in nodes):
        break

# Print final routing tables
for node in nodes:
    node.display_routing_info()
