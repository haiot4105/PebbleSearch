'''
Code from https://www.geeksforgeeks.org/biconnected-components/
'''

from collections import defaultdict
  
class Graph:
    '''
    This class represents an directed graph
    using adjacency list representation
    '''
  
    def __init__(self, vertices):
        # No. of vertices
        self.V = vertices
         
        # default dictionary to store graph
        self.graph = defaultdict(list)
         
        # time is used to find discovery times
        self.Time = 0
         
        # Count is number of biconnected components
        self.count = 0
  
    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)
        self.graph[v].append(u)
 

    def BCCUtil(self, u, parent, low, disc, st):
        '''A recursive function that finds and prints strongly connected
        components using DFS traversal
        u --> The vertex to be visited next
        disc[] --> Stores discovery times of visited vertices
        low[] -- >> earliest visited vertex (the vertex with minimum
                discovery time) that can be reached from subtree
                rooted with current vertex
        st -- >> To store visited edges'''

        # Count of children in current node
        children = 0
 
        # Initialize discovery time and low value
        disc[u] = self.Time
        low[u] = self.Time
        self.Time += 1
 
 
        # Recur for all the vertices adjacent to this vertex
        for v in self.graph[u]:
            # If v is not visited yet, then make it a child of u
            # in DFS tree and recur for it
            if disc[v] == -1 :
                parent[v] = u
                children += 1
                st.append((u, v)) # store the edge in stack
                self.BCCUtil(v, parent, low, disc, st)
 
                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                # Case 1 -- per Strongly Connected Components Article
                low[u] = min(low[u], low[v])
 
                # If u is an articulation point, pop
                # all edges from stack till (u, v)
                if parent[u] == -1 and children > 1 or parent[u] != -1 and low[v] >= disc[u]:
                    self.count += 1 # increment count
                    w = -1
                    while w != (u, v):
                        w = st.pop()
             
            elif v != parent[u] and low[u] > disc[v]:
                '''Update low value of 'u' only of 'v' is still in stack
                (i.e. it's a back edge, not cross edge).
                Case 2
                -- per Strongly Connected Components Article'''
 
                low[u] = min(low [u], disc[v])
     
                st.append((u, v))
 

    def BCC(self):
        '''
        The function to do DFS traversal.
        It uses recursive BCCUtil()
        '''         
        # Initialize disc and low, and parent arrays
        disc = [-1] * (self.V)
        low = [-1] * (self.V)
        parent = [-1] * (self.V)
        st = []
 
        # Call the recursive helper function to
        # find articulation points
        # in DFS tree rooted with vertex 'i'
        for i in range(self.V):
            if disc[i] == -1:
                self.BCCUtil(i, parent, low, disc, st)
 
            # If stack is not empty, pop all edges from stack
            if st:
                self.count = self.count + 1
 
                while st:
                    w = st.pop()
 