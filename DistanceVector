#!/usr/bin/env python3

import sys
import math

INF = math.inf

class Graph:
    # Represents a network graph with weighted edges between routers.
    def __init__(self):
        self.vertex_dict = {}
    def add_edge(self, v1, v2, weight):
        # Add a bidirectional weighted edge between two routers.
        if v1 not in self.vertex_dict:
            self.vertex_dict[v1] = {}
        if v2 not in self.vertex_dict:
            self.vertex_dict[v2] = {}
        self.vertex_dict[v1][v2] = weight
        self.vertex_dict[v2][v1] = weight
    def remove_edge(self, v1, v2):
        # Remove the edge between two routers.
        if v1 not in self.vertex_dict or v2 not in self.vertex_dict:
            return
        if v2 in self.vertex_dict[v1]:
            del self.vertex_dict[v1][v2]
        if v1 in self.vertex_dict[v2]:
            del self.vertex_dict[v2][v1]
    def get_neighbors(self, v):
        # Get all neighbors of a router.
        return self.vertex_dict.get(v, {})

class Router:
    def __init__(self, name, all_nodes):
        self.name = name
        self.distance_table = {}
        self.routing_table = {}
        self.changed = True
        
        # Initialize distance table
        other_nodes = [n for n in all_nodes if n != name]
        for dest in other_nodes:
            self.distance_table[dest] = {}
            for via in other_nodes:
                self.distance_table[dest][via] = INF

    def update_from_graph(self, graph, all_routers):
        neighbors = graph.get_neighbors(self.name)
        old_changed = self.changed
        
        # Update direct neighbor costs
        for neighbor, cost in neighbors.items():
            if neighbor in self.distance_table:
                old_cost = self.distance_table[neighbor][neighbor]
                self.distance_table[neighbor][neighbor] = cost
                if old_cost != cost:
                    self.changed = True
        
        # Set unreachable neighbors to infinity
        for router in all_routers:
            if router.name != self.name and router.name not in neighbors:
                for dest in self.distance_table:
                    old_cost = self.distance_table[dest][router.name]
                    self.distance_table[dest][router.name] = INF
                    if old_cost != INF:
                        self.changed = True

    def receive_update(self, sender_name, sender_distances):
        if sender_name not in self.distance_table:
            return
            
        cost_to_sender = self.distance_table[sender_name][sender_name]
        
        for dest in self.distance_table:
            if dest == sender_name:
                continue
                
            old_cost = self.distance_table[dest][sender_name]
            min_cost_via_sender = min(sender_distances[dest].values()) if dest in sender_distances else INF
            new_cost = cost_to_sender + min_cost_via_sender
            
            self.distance_table[dest][sender_name] = new_cost
            if old_cost != new_cost:
                self.changed = True

    def get_distance_table_copy(self):
        # Manual deep copy without using copy library
        result = {}
        for dest in self.distance_table:
            result[dest] = {}
            for via in self.distance_table[dest]:
                result[dest][via] = self.distance_table[dest][via]
        return result

    def print_distance_table(self):
        nodes = sorted(self.distance_table.keys())
        header = [' '] + nodes
        print('\t'.join(header))
        
        for dest in nodes:
            row = [dest] + [str(self.distance_table[dest][via]).replace('inf', 'INF') for via in nodes]
            print('\t'.join(row))

    def create_routing_table(self):
        self.routing_table = {}
        for dest in self.distance_table:
            min_cost = INF
            next_hop = None
            for via in self.distance_table[dest]:
                if self.distance_table[dest][via] < min_cost:
                    min_cost = self.distance_table[dest][via]
                    next_hop = via
            self.routing_table[dest] = (next_hop, min_cost)

    def print_routing_table(self):
        self.create_routing_table()
        print(f"Routing Table of router {self.name}:")
        for dest in sorted(self.routing_table.keys()):
            next_hop, cost = self.routing_table[dest]
            print(f"{dest},{next_hop},{cost}")
        print()

def run_distance_vector(graph, routers):
    t = 1
    
    while True:
        # Store previous state manually
        prev_tables = {}
        for router in routers:
            prev_tables[router.name] = router.get_distance_table_copy()
        
        # Send updates
        updates = []
        for router in routers:
            if router.changed:
                neighbors = graph.get_neighbors(router.name)
                for neighbor_name in neighbors:
                    updates.append((neighbor_name, router.name, router.get_distance_table_copy()))
                router.changed = False
        
        # Process updates
        for receiver_name, sender_name, distance_table in updates:
            for router in routers:
                if router.name == receiver_name:
                    router.receive_update(sender_name, distance_table)
                    break
        
        # Check convergence
        converged = True
        for router in routers:
            if router.name not in prev_tables:
                converged = False
                break
            for dest in router.distance_table:
                for via in router.distance_table[dest]:
                    if router.distance_table[dest][via] != prev_tables[router.name][dest][via]:
                        converged = False
                        break
                if not converged:
                    break
            if not converged:
                break
        
        if converged:
            break
        
        # Print current state
        for router in routers:
            print(f"Distance Table of router {router.name} at t={t}:")
            router.print_distance_table()
            print()
        
        t += 1
    
    return t

# Main execution
nodes_list = []
graph = Graph()

# Read nodes
line = sys.stdin.readline().strip()
while line != "START":
    nodes_list.append(line)
    line = sys.stdin.readline().strip()

# Read edges
line = sys.stdin.readline().strip()
while line != "UPDATE":
    node1, node2, weight = line.split()
    graph.add_edge(node1, node2, int(weight))
    line = sys.stdin.readline().strip()

# Initialize routers
routers = []
for node in nodes_list:
    router = Router(node, nodes_list)
    routers.append(router)

# Update routers with initial graph state
for router in routers:
    router.update_from_graph(graph, routers)

# Print initial state
for router in routers:
    print(f"Distance Table of router {router.name} at t=0:")
    router.print_distance_table()
    print()

# Run algorithm to convergence
t = run_distance_vector(graph, routers)

# Print final routing tables
for router in routers:
    router.print_routing_table()

# Process graph updates
while True:
    line = sys.stdin.readline().strip()
    if line == "END":
        break
    
    node1, node2, weight = line.split()
    if int(weight) == -1:
        graph.remove_edge(node1, node2)
    else:
        graph.add_edge(node1, node2, int(weight))

# Store state before update
prev_tables = {}
for router in routers:
    prev_tables[router.name] = router.get_distance_table_copy()

# Update routers with new graph state
for router in routers:
    router.update_from_graph(graph, routers)
    # Update with current routing tables
    neighbors = graph.get_neighbors(router.name)
    for other_router in routers:
        if other_router.name in neighbors and other_router.name != router.name:
            for dest in other_router.routing_table:
                if dest != router.name:
                    cost_to_neighbor = router.distance_table[other_router.name][other_router.name]
                    neighbor_to_dest = other_router.routing_table[dest][1]
                    old_cost = router.distance_table[dest][other_router.name]
                    new_cost = cost_to_neighbor + neighbor_to_dest
                    router.distance_table[dest][other_router.name] = new_cost
                    if old_cost != new_cost:
                        router.changed = True

# Check if anything changed
any_changed = False
for router in routers:
    for dest in router.distance_table:
        for via in router.distance_table[dest]:
            if router.distance_table[dest][via] != prev_tables[router.name][dest][via]:
                any_changed = True
                break
        if any_changed:
            break
    if any_changed:
        break

if not any_changed:
    sys.exit()

# Print state after update
for router in routers:
    print(f"Distance Table of router {router.name} at t={t}:")
    router.print_distance_table()
    print()

# Continue to convergence
run_distance_vector(graph, routers)

# Print final routing tables
for router in routers:
    router.print_routing_table()
