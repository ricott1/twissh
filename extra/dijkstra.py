"""
1. Mark all nodes unvisited. Create a set of all the unvisited nodes called the unvisited set.

2. Assign to every node a tentative distance value: set it to zero for our initial node and to infinity for all other nodes. Set the initial node as current.[16]

3. For the current node, consider all of its unvisited neighbours and calculate their tentative distances through the current node. Compare the newly calculated tentative distance to the current assigned value and assign the smaller one. For example, if the current node A is marked with a distance of 6, and the edge connecting it with a neighbour B has length 2, then the distance to B through A will be 6 + 2 = 8. If B was previously marked with a distance greater than 8 then change it to 8. Otherwise, the current value will be kept.

4. When we are done considering all of the unvisited neighbours of the current node, mark the current node as visited and remove it from the unvisited set. A visited node will never be checked again.

5. If the destination node has been marked visited (when planning a route between two specific nodes) or if the smallest tentative distance among the nodes in the unvisited set is infinity (when planning a complete traversal; occurs when there is no connection between the initial node and remaining unvisited nodes), then stop. The algorithm has finished.

6. Otherwise, select the unvisited node that is marked with the smallest tentative distance, set it as the new "current node", and go back to step 3.
"""

import copy, math

nested_dict = lambda: collections.defaultdict(nested_dict)

class Dijkstra(object):
	def __init__(self, _entity, _target=None):
		self.entity = _entity
		self.target = _target
		
		self.distance = 0
		self.unvisited_set = nested_dict()
		_map = copy.deepcopy(self.entity.location.content)
		for x in _map:
			for y in _map[x]:
				for z in _map[x][y]:
					self.unvisited_set[x][y][z] = math.inf

		self.visit(self.entity.position)

	def visit(self, pos):
		self.current = pos
		x, y, z = self.current
		del self.unvisited_set[x][y][z]

	def next(self):
		if not target:
			return

		_loc = self.entity.location
		x, y, z = self.current
		neighbours = []
		for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx + dy) %2 == 0:
                    continue
                pos = (x+dx, y+dy, z)
                if _loc.is_empty(pos) and x in self.unvisited_set and y in self.unvisited_set[x] and z in self.unvisited_set[x][y]:
                	neighbours.append(pos)
                	self.unvisited_set[x][y][z] = min(1, self.unvisited_set[x][y][z])






