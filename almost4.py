#!/usr/bin/env python3

import sys
import math

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
    def __init__(self, name):
        self.name = name
        self.distance_table = {}
        self.routing_table = {}
        self.changed = False
    
    def initialize_distance_table(self, all_routers, graph):
        # Initialize distance table for all destinations except self
        other_routers = [r for r in all_routers if r != self.name]
        
        for dest in other_routers:
            self.distance_table[dest] = {}
            for via in other_routers:
                if via == dest:
                    # Direct neighbor cost or infinity
                    neighbors = graph.get_neighbors(self.name)
                    self.distance_table[dest][via] = neighbors.get(dest, math.inf)
                else:
                    self.distance_table[dest][via] = math.inf
        
        self.changed = True
    
    def update_distance_table(self, sender_name, sender_distances):
        if sender_name == self.name:
            return
            
        old_table = self.get_distance_table_copy()
        
        # Get cost to sender
        cost_to_sender = self.distance_table.get(sender_name, {}).get(sender_name, math.inf)
        
        # Update distances via this sender
        for dest in self.distance_table:
            if dest == sender_name:
                continue
                
            if dest in sender_distances:
                # Find minimum cost from sender to destination
                min_sender_cost = min(sender_distances[dest].values())
                new_cost = cost_to_sender + min_sender_cost
                self.distance_table[dest][sender_name] = new_cost
        
        # Check if anything changed
        if self.distance_table != old_table:
            self.changed = True
    
    def get_distance_table_copy(self):
        result = {}
        for dest in self.distance_table:
            result[dest] = {}
            for via in self.distance_table[dest]:
                result[dest][via] = self.distance_table[dest][via]
        return result
    
    def print_distance_table(self, time_step):
        print(f"Distance Table of router {self.name} at t={time_step}:")
        
        if not self.distance_table:
            print()
            return
            
        destinations = sorted(self.distance_table.keys())
        
        # Print header
        header = [' '] + destinations
        print('\t'.join(header))
        
        # Print rows
        for dest in destinations:
            row_values = []
            for via in destinations:
                cost = self.distance_table[dest][via]
                if cost == math.inf:
                    row_values.append('INF')
                else:
                    row_values.append(str(int(cost)))
            row = [dest] + row_values
            print('\t'.join(row))
        print()
    
    def create_routing_table(self):
        self.routing_table = {}
        
        for dest in sorted(self.distance_table.keys()):
            min_cost = math.inf
            next_hop = None
            
            # Find minimum cost path in alphabetical order of via nodes
            for via in sorted(self.distance_table[dest].keys()):
                cost = self.distance_table[dest][via]
                if cost < min_cost:
                    min_cost = cost
                    next_hop = via
            
            if next_hop is not None and min_cost != math.inf:
                self.routing_table[dest] = (next_hop, int(min_cost))
            else:
                self.routing_table[dest] = ('INF', 'INF')
    
    def print_routing_table(self):
        self.create_routing_table()
        print(f"Routing Table of router {self.name}:")
        
        for dest in sorted(self.routing_table.keys()):
            next_hop, cost = self.routing_table[dest]
            print(f"{dest},{next_hop},{cost}")
        print()

def main():
    # Read router names
    router_names = []
    while True:
        line = sys.stdin.readline().strip()
        if line == "START":
            break
        router_names.append(line)
    
    # Initialize graph and routers
    graph = Graph()
    routers = {}
    
    for name in router_names:
        routers[name] = Router(name)
    
    # Read initial topology
    while True:
        line = sys.stdin.readline().strip()
        if line == "UPDATE":
            break
        
        parts = line.split()
        if len(parts) == 3:
            v1, v2, weight = parts[0], parts[1], int(parts[2])
            if weight == -1:
                graph.remove_edge(v1, v2)
            else:
                graph.add_edge(v1, v2, weight)
    
    # Initialize distance tables
    for router in routers.values():
        router.initialize_distance_table(router_names, graph)
    
    # Run initial convergence
    time_step = 0
    
    # Print initial state
    for name in sorted(router_names):
        routers[name].print_distance_table(time_step)
    
    # Convergence loop
    time_step = 1
    while True:
        # Reset change flags
        any_changed = False
        
        # Each router sends its distance vector to neighbors
        updates = []
        for router in routers.values():
            if router.changed:
                neighbors = graph.get_neighbors(router.name)
                for neighbor_name in neighbors:
                    if neighbor_name in routers:
                        updates.append((neighbor_name, router.name, router.get_distance_table_copy()))
                router.changed = False
        
        # Process all updates
        for receiver_name, sender_name, distance_table in updates:
            routers[receiver_name].update_distance_table(sender_name, distance_table)
            if routers[receiver_name].changed:
                any_changed = True
        
        if not any_changed:
            break
        
        # Print current state
        for name in sorted(router_names):
            routers[name].print_distance_table(time_step)
        
        time_step += 1
    
    # Print final routing tables
    for name in sorted(router_names):
        routers[name].print_routing_table()
    
    # Process updates
    updates_made = False
    while True:
        line = sys.stdin.readline().strip()
        if line == "END":
            break
        
        parts = line.split()
        if len(parts) == 3:
            v1, v2, weight = parts[0], parts[1], int(parts[2])
            
            # Add new routers if they don't exist
            if v1 not in routers:
                router_names.append(v1)
                routers[v1] = Router(v1)
            if v2 not in routers:
                router_names.append(v2)
                routers[v2] = Router(v2)
            
            if weight == -1:
                graph.remove_edge(v1, v2)
            else:
                graph.add_edge(v1, v2, weight)
            
            updates_made = True
    
    if not updates_made:
        return
    
    # Reinitialize all routers after topology change
    router_names.sort()
    for router in routers.values():
        router.initialize_distance_table(router_names, graph)
    
    # Print state after update
    for name in sorted(router_names):
        routers[name].print_distance_table(time_step)
    
    time_step += 1
    
    # Run convergence again
    while True:
        any_changed = False
        
        updates = []
        for router in routers.values():
            if router.changed:
                neighbors = graph.get_neighbors(router.name)
                for neighbor_name in neighbors:
                    if neighbor_name in routers:
                        updates.append((neighbor_name, router.name, router.get_distance_table_copy()))
                router.changed = False
        
        for receiver_name, sender_name, distance_table in updates:
            routers[receiver_name].update_distance_table(sender_name, distance_table)
            if routers[receiver_name].changed:
                any_changed = True
        
        if not any_changed:
            break
        
        for name in sorted(router_names):
            routers[name].print_distance_table(time_step)
        
        time_step += 1
    
    # Print final routing tables
    for name in sorted(router_names):
        routers[name].print_routing_table()

if __name__ == "__main__":
    main()
