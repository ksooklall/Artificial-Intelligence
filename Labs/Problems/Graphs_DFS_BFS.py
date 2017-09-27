class Node:
	def __init__(self, name):
		self.name = name
		self.distance = 9999
		self.visited = False
		self.neighbors = []

	def add_neighbors(self, node):
		if node not in self.neighbors:
			self.neighbors.append(node)
			self.neighbors.sort()

class Graph:
	# key: str(name) value: object(Node)
	graph = {}

	def add_node(self, node):
		if isinstance(node, Node) and node.name not in self.graph:
			self.graph[node.name] = node

	def add_edges(self, uu, vv):
		if uu in self.graph and vv in self.graph:
			self.graph[uu].add_neighbors(vv)
			self.graph[vv].add_neighbors(uu)

	def get_node(self, node):
		return self.graph[node]
		
	def bfs(self, begin):
		q = []
		begin.distance = 0
		begin.visited = True
		for i in begin.neighbors:		
			self.graph[i].distance = begin.distance + 1
			q.append(i)
			
		while len(q) > 0:
			s = q.pop(0)
			node_u = self.graph[s]
			node_u.visited = True
			
			for n in node_u.neighbors:
				node_v = self.graph[n]
				if not node_v.visited:
					q.append(node_v.name)
					if node_v.distance > node_u.distance + 1:
						node_v.distance = node_u.distance + 1
			
	def dfs(self, begin):
		pass
				
	def print_graph(self):
		for node, value in self.graph.items():
			print('Node: {} Neighbors: {} DistFromSource: {}'.format(node, value.neighbors, value.distance))
			
if __name__ == '__main__':	
	g = Graph()
	edges = ['AB', 'AE', 'BF', 'CG', 'DE', 'DH', 'EH', 'FG', 'FJ', 'FI', 'HI', 'JG']
	for c in range(ord('A'), ord('K')):
		g.add_node(Node(chr(c)))

	for edge in edges:
		g.add_edges(edge[0], edge[1])
	g.bfs(g.get_node('A'))
	g.print_graph()
