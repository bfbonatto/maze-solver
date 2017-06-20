#@def: Maze: solves a maze
class Maze:
	def __init__(self, txt_maze, start, finish, dim):
		self.start = (0, start)
		self.finish = (len(txt_maze) - 1, finish)
		self.dim = dim
		self.txt_maze = []
		self.maze = {}
		for i in range(self.dim):
			self.txt_maze.append([])
			for j in range(self.dim):
				self.txt_maze[i].append(txt_maze[i][j])
				if txt_maze[i][j] == ' ':
					self.maze[(i, j)] = []
					if i > 0 and txt_maze[i - 1][j] == ' ':
						self.maze[(i, j)].append((i - 1, j))
					if i < self.dim - 1 and txt_maze[i + 1][j] == ' ':
						self.maze[(i, j)].append((i + 1, j))
					if j > 0 and txt_maze[i][j - 1] == ' ':
						self.maze[(i, j)].append((i, j - 1))
					if j < self.dim - 1 and txt_maze[i][j + 1] == ' ':
						self.maze[(i, j)].append((i, j + 1))
		self.optimize()
	
	#@def:	delta:
	#			phi(v) | v in m; m is graph
	@staticmethod
	def delta(v, m):
		d = 0
		(i, j) = v
		if m[i + 1][j] == ' ':
			d += 1
		if m[i - 1][j] == ' ':
			d += 1
		if m[i][j + 1] == ' ':
			d += 1
		if m[i][j - 1] == ' ':
			d += 1
		return d
	
	#@def:	distance:
	#			euclidean distance of p1 to p2
	@staticmethod
	def distance(p1,p2):
		return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(1/2)
	
	#@def:	prepare_file:
	#			formats @filename into a readable format
	@staticmethod
	def prepare_file(filename):
		f = open(filename,'r')
		m = []
		for line in f:
			aux = []
			for c in line:
				if c == '*':
					aux.append(c)
				else:
					aux.append(' ')
			m.append(aux)
		f.close()
		return m
	
	#@def:	optimize:
	#			optimizes the graph, eliminating all 'uninteresting' vertexes, leaving only dead-ends, intersections
	#			and turns
	def optimize(self):
		self.maze = {}
		self.maze[self.start] = []
		self.maze[self.finish] = []
		
		for i in range(1, self.dim - 1):
			for j in range(1, self.dim - 1):
				if self.txt_maze[i][j] == ' ':
					if not Maze.delta((i, j), self.txt_maze) == 2:
						self.maze[(i, j)] = []
					elif self.txt_maze[i - 1][j] != self.txt_maze[i + 1][j] or self.txt_maze[i][j - 1] != self.txt_maze[i][j + 1]:
						self.maze[(i, j)] = []
		
		for i in range(self.dim):
			actual = (-1, -1)
			actual2 = (-1, -1)
			for j in range(self.dim):
				if self.txt_maze[i][j] == '*':
					actual = (-1, -1)
				elif (i, j) in self.maze:
					if actual == (-1, -1):
						actual = (i, j)
					else:
						self.maze[actual].append((i, j))
						self.maze[(i, j)].append(actual)
						actual = (i, j)
				if self.txt_maze[j][i] == '*':
					actual2 = (-1, -1)
				elif (j, i) in self.maze:
					if actual2 == (-1, -1):
						actual2 = (j, i)
					else:
						self.maze[actual2].append((j, i))
						self.maze[(j, i)].append(actual2)
						actual2 = (j, i)
	
	#@def:	depth_search:
	#			solves the maze using a naive depth first search, implemented using a priority stack instead of recursiion
	#			to improve readability and maintain consistency of implementation across class
	def depth_search(self):
		todo = []
		done = []
		solution = []
		actual = self.start
		while not actual == self.finish:
			self.print_solution(solution)
			print()
			print()
			print()
			if actual not in done:
				done.append(actual)
			solution.append(actual)
			back = True
			for neighbour in self.maze[actual]:
				if neighbour not in done:
					todo.append(neighbour)
					back = False
			if back:
				solution.pop()
			actual = todo.pop()
			
		solution.append(self.finish)
		return solution
	
	#@def:	dijjstra:
	#			solves the maze with a simple implementations of Dijkstra's algorithm
	def dijkstra(self):
		distances = {}
		for n in self.maze:
			distances[n] = 10000000000
		distances[self.start] = 0
		todo = list(self.maze.keys())
		actual = self.start
		prev = {}
		while not actual == self.finish:
			for neighbour in self.maze[actual]:
				d = self.distance(actual,neighbour) + distances[actual]
				if distances[neighbour] > d:
					distances[neighbour] = d
					prev[neighbour] = actual
			todo.remove(actual)
			actual = [n for n in todo if distances[n] == min([distances[x] for x in todo])][0]
		s = []
		while actual in prev:
			s.append(actual)
			actual = prev[actual]
		s.append(self.start)
		s.reverse()
		return s
	
	def final_solution_ants(self,pheromones):
		actual = self.start
		solution = []
		while not actual == self.finish:
			solution.append(actual)
			next_pheromones = [pheromones[(actual,p)] for p in self.maze[actual] if p not in solution]
			actual = [n for n in self.maze[actual] if n not in solution and pheromones[(actual,n)] == max(next_pheromones)].pop()
		solution.append(self.finish)
		return solution
	
	def construct_solution_ant(self,pheromones):
		import random
		
		actual = self.start
		solution = []
		while not actual == self.finish:
			solution.append(actual)
			neighbours = [n for n in self.maze[actual] if n not in solution]
			if neighbours == []:
				return []
			neighbour_pheromones = [pheromones[(actual,p)] for p in neighbours]
			total_pheromones = sum(neighbour_pheromones)
			pheromone_percent = [p/total_pheromones for p in neighbour_pheromones]
			r = random.random()
			for i in range(len(pheromone_percent)):
				if r <= sum(pheromone_percent[0:i+1]):
					actual = neighbours[i]
					break
		solution.append(self.finish)
		
		s = sum([Maze.distance(solution[i],solution[i+1]) for i in range(len(solution)-1)])
		for i in range(len(solution)-1):
			pheromones[(solution[i],solution[i+1])] += 10/s
		
		return solution
	
	@staticmethod
	def pheromone_decay(pheromones):
		for (i,j) in pheromones:
			pheromones[(i,j)] = pheromones[(i,j)]/2
	
	def ants(self,iterations,number_of_ants):
		pheromones = {}
		for n in self.maze:
			for nn in self.maze[n]:
				pheromones[(n,nn)] = 1
		for i in range(iterations):
			for j in range(number_of_ants):
				self.construct_solution_ant(pheromones)
			Maze.pheromone_decay(pheromones)
		return self.final_solution_ants(pheromones)
		
	#@def:	print_solution:
	#			takes a solution, @solution, and prints it over the maze
	def print_solution(self, solution):
		txt_maze = []
		for l in self.txt_maze:
			aux = []
			for c in l:
				aux.append(c)
			txt_maze.append(aux)
			
		for i in range(len(solution) - 1):
			if solution[i][0] == solution[i + 1][0]:
				for j in range(solution[i][1], solution[i + 1][1] + 1):
					txt_maze[solution[i][0]][j] = '@'
				for j in range(solution[i+1][1], solution[i][1] + 1):
					txt_maze[solution[i][0]][j] = '@'
			else:
				for j in range(solution[i][0], solution[i + 1][0] + 1):
					txt_maze[j][solution[i][1]] = '@'
				for j in range(solution[i+1][0], solution[i][0] + 1):
					txt_maze[j][solution[i][1]] = '@'
		
		for l in txt_maze:
			for c in l:
				print(c, end='')
			print()
