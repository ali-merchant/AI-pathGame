import tkinter as tk
from tkinter import ttk
from collections import deque

class PathfinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Pathfinder")
        self.root.geometry("900x750")
        
        self.rows = 8
        self.cols = 10
        self.cell_size = 50
        
        self.start = (5, 7)
        self.target = (6, 1)
        self.walls = [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5)]
        
        #colors
        self.empty_col = 'white'
        self.wall_col = 'black'
        self.start_col = 'blue'
        self.target_col = 'green'
        self.frontier_col = 'red'
        self.explored_col = 'lightblue'
        self.path_col = 'yellow'
        
        self.frontier = []
        self.explored = []
        self.path = []
        
        self.searching = False
        self.q = None
        self.stk = None
        self.visited = None
        self.algo = ""
        self.steps = 0
        self.delay = 500

        self.depth_lim = 0
        self.max_depth = 20

                
        
        self.fwd_q = None
        self.bwd_q = None
        self.fwd_visited = None
        self.bwd_visited = None
        self.fwd_parent = None
        self.bwd_parent = None
        
        self.setup_ui()
        
    def setup_ui(self):
        top = tk.Frame(self.root)
        top.pack(pady=10)
        
        tk.Label(top, text="Algorithm:", font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        self.algo_var = tk.StringVar(value="BFS")
        dropdown = ttk.Combobox(top, textvariable=self.algo_var, 
                                values=["BFS", "DFS", "UCS","DLS","IDDFS","Bidirectional"], 
                                state='readonly', width=15)
        dropdown.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(top, text="Start", command=self.init_search, 
                                    bg='lightgreen', font=('Arial', 10, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(top, text="Reset", command=self.reset_grid, 
                                    bg='orange', font=('Arial', 10))
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.status = tk.Label(self.root, text="Ready", font=('Arial', 10), fg='blue')
        self.status.pack(pady=5)
        
        self.canvas = tk.Canvas(self.root, width=self.cols * self.cell_size,
                                height=self.rows * self.cell_size, 
                                bg='white', borderwidth=2, relief='solid')
        self.canvas.pack(pady=10)
        
        #legend
        leg = tk.Frame(self.root)
        leg.pack(pady=10)
        
        self.make_legend(leg, "Start", self.start_col)
        self.make_legend(leg, "Target", self.target_col)
        self.make_legend(leg, "Wall", self.wall_col)
        self.make_legend(leg, "Frontier", self.frontier_col)
        self.make_legend(leg, "Explored", self.explored_col)
        self.make_legend(leg, "Path", self.path_col)
        
        self.draw()
    
    def make_legend(self, parent, txt, col):
        item = tk.Frame(parent)
        item.pack(side=tk.LEFT, padx=10)
        box = tk.Label(item, bg=col, width=2, height=1, relief='solid', borderwidth=1)
        box.pack(side=tk.LEFT, padx=2)
        tk.Label(item, text=txt, font=('Arial', 9)).pack(side=tk.LEFT)
    
    def draw(self):
        self.canvas.delete("all")
        
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                col = self.empty_col
                
                if (r, c) == self.start:
                    col = self.start_col
                elif (r, c) == self.target:
                    col = self.target_col
                elif (r, c) in self.walls:
                    col = self.wall_col
                elif (r, c) in self.path:
                    col = self.path_col
                elif (r, c) in self.frontier:
                    col = self.frontier_col
                elif (r, c) in self.explored:
                    col = self.explored_col
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=col, outline='gray')
    
    def get_nbrs(self, pos):
        r, c = pos
        nbrs = []
        
        #up
        if r - 1 >= 0 and (r - 1, c) not in self.walls:
            nbrs.append((r - 1, c))
        #right
        if c + 1 < self.cols and (r, c + 1) not in self.walls:
            nbrs.append((r, c + 1))
        #down
        if r + 1 < self.rows and (r + 1, c) not in self.walls:
            nbrs.append((r + 1, c))
        #down-right diagonal
        if r + 1 < self.rows and c + 1 < self.cols and (r + 1, c + 1) not in self.walls:
            nbrs.append((r + 1, c + 1))
        #left
        if c - 1 >= 0 and (r, c - 1) not in self.walls:
            nbrs.append((r, c - 1))
        #up-left diagonal
        if r - 1 >= 0 and c - 1 >= 0 and (r - 1, c - 1) not in self.walls:
            nbrs.append((r - 1, c - 1))
        
        return nbrs
    
    def calc_cost(self, p1, p2):
        r1, c1 = p1
        r2, c2 = p2
        
        dr = r2 - r1
        dc = c2 - c1
        
        if dr == -1 and dc == 0:  # U
            return 1.0
        elif dr == 0 and dc == 1:  # R
            return 2.0
        elif dr == 1 and dc == 0:  # D
            return 3.0
        elif dr == 1 and dc == 1:  # DR
            return 4.0
        elif dr == 0 and dc == -1:  # L
            return 5.0
        elif dr == -1 and dc == -1:  # UL
            return 6.0
        else:
            return 1.0

    def reset_grid(self):
        self.frontier = []
        self.explored = []
        self.path = []
        self.searching = False
        self.q = None
        self.stk = None
        self.visited = None
        self.steps = 0
        self.draw()
        self.status.config(text="Ready", fg='blue')
        self.start_btn.config(state='normal')
        self.depth_lim = 0

        self.fwd_q = None
        self.bwd_q = None
        self.fwd_visited = None
        self.bwd_visited = None
        self.fwd_parent = None
        self.bwd_parent = None
        
    
    def init_search(self):
        self.algo = self.algo_var.get()
        
        self.frontier = []
        self.explored = []
        self.path = []
        self.steps = 0
        self.draw()
        
        if self.algo == "BFS":
            self.q = deque()
            self.q.append((self.start, [self.start]))
            self.visited = set()
            self.visited.add(self.start)
            self.searching = True
            self.status.config(text="BFS started...", fg='green')
            self.start_btn.config(state='disabled')
            self.root.after(self.delay, self.next_step)
            
        elif self.algo == "DFS":
            self.stk = []
            self.stk.append((self.start, [self.start]))
            self.visited = set()
            self.visited.add(self.start)
            self.searching = True
            self.status.config(text="DFS started...", fg='green')
            self.start_btn.config(state='disabled')
            self.root.after(self.delay, self.next_step)
        elif self.algo == "UCS":
            self.q = [(0, self.start, [self.start])]
            self.visited = {}
            self.visited[self.start] = 0
            self.searching = True
            self.status.config(text="UCS started...", fg='green')
            self.start_btn.config(state='disabled')
            self.root.after(self.delay, self.next_step)
        elif self.algo == "DLS":
            self.depth_lim = 20
            self.stk = []
            self.stk.append((self.start, [self.start], 0))
            self.visited = set()
            self.searching = True
            self.status.config(text="DLS started (limit=" + str(self.depth_lim) + ")...", fg='green')
            self.start_btn.config(state='disabled')
            self.root.after(self.delay, self.next_step)

        elif self.algo == "IDDFS":
            
            self.depth_lim = 0
            self.stk = []
            self.stk.append((self.start, [self.start], 0))
            self.visited = set()
            self.searching = True
            self.status.config(text="IDDFS started (depth=" + str(self.depth_lim) + ")...", fg='green')
            self.start_btn.config(state='disabled')
            self.root.after(self.delay, self.next_step)
        elif self.algo == "Bidirectional":
            self.fwd_q = deque()
            self.bwd_q = deque()
            self.fwd_q.append(self.start)
            self.bwd_q.append(self.target)
            self.fwd_visited = {self.start: None}
            self.bwd_visited = {self.target: None}
            self.fwd_parent = {self.start: None}
            self.bwd_parent = {self.target: None}
            self.searching = True
            self.status.config(text="Bidirectional started...", fg='green')
            self.start_btn.config(state='disabled')
            self.root.after(self.delay, self.next_step)

    def next_step(self):
        if not self.searching:
            return
        
        if self.algo == "BFS":
            self.do_bfs()
        elif self.algo == "DFS":
            self.do_dfs()
        elif self.algo == "UCS":
            self.do_ucs()
        elif self.algo == "DLS":
            self.do_dls()
        elif self.algo == "IDDFS":
            self.do_iddfs()
        elif self.algo == "Bidirectional":
            self.do_bidirectional()
    def do_bfs(self):
        if len(self.q) == 0:
            self.status.config(text="No path!", fg='red')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        n, p = self.q.popleft()
        self.steps += 1
        
        self.frontier = []
        for node, path in self.q:
            self.frontier.append(node)
        
        self.draw()
        
        if n == self.target:
            self.path = p
            self.frontier = []
            self.draw()
            self.status.config(text="Found! Length: " + str(len(p)) + 
                              " Steps: " + str(self.steps), fg='darkgreen')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        if n != self.start:
            self.explored.append(n)
        
        nbrs = self.get_nbrs(n)
        for nbr in nbrs:
            if nbr not in self.visited:
                self.visited.add(nbr)
                new_p = p + [nbr]
                self.q.append((nbr, new_p))
        
        self.status.config(text="Step " + str(self.steps) + " | Current: " + 
                          str(n) + " | Frontier: " + str(len(self.q)), fg='blue')
        
        if self.searching:
            self.root.after(self.delay, self.next_step)
    
    def do_dfs(self):
        if len(self.stk) == 0:
            self.status.config(text="No path!", fg='red')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        n, p = self.stk.pop()
        self.steps += 1
        
        self.frontier = []
        for node, path in self.stk:
            self.frontier.append(node)
        
        self.draw()
        
        if n == self.target:
            self.path = p
            self.frontier = []
            self.draw()
            self.status.config(text="Found! Length: " + str(len(p)) + 
                              " Steps: " + str(self.steps), fg='darkgreen')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        if n != self.start:
            self.explored.append(n)
        
        nbrs = self.get_nbrs(n)
        for nbr in nbrs:
            if nbr not in self.visited:
                self.visited.add(nbr)
                new_p = p + [nbr]
                self.stk.append((nbr, new_p))
        
        self.status.config(text="Step " + str(self.steps) + " | Current: " + 
                          str(n) + " | Frontier: " + str(len(self.stk)), fg='blue')
        
        if self.searching:
            self.root.after(self.delay, self.next_step)

    def do_ucs(self):
        if len(self.q) == 0:
            self.status.config(text="No path!", fg='red')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        #find min cost
        min_i = 0
        min_c = self.q[0][0]
        for i in range(len(self.q)):
            if self.q[i][0] < min_c:
                min_c = self.q[i][0]
                min_i = i
        
        cost, n, p = self.q.pop(min_i)
        self.steps += 1
        
        self.frontier = []
        for c, node, path in self.q:
            self.frontier.append(node)
        
        self.draw()
        
        if n == self.target:
            self.path = p
            self.frontier = []
            self.draw()
            self.status.config(text="Found! Cost: " + str(round(cost, 2)) + 
                              " Steps: " + str(self.steps), fg='darkgreen')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        if n != self.start:
            self.explored.append(n)
        
        nbrs = self.get_nbrs(n)
        for nbr in nbrs:
            edge_c = self.calc_cost(n, nbr)
            new_c = cost + edge_c
            
            if nbr not in self.visited or new_c < self.visited[nbr]:
                self.visited[nbr] = new_c
                new_p = p + [nbr]
                self.q.append((new_c, nbr, new_p))
        
        self.status.config(text="Step " + str(self.steps) + " | Cost: " + 
                          str(round(cost, 2)) + " | Frontier: " + str(len(self.q)), fg='blue')
        
        if self.searching:
            self.root.after(self.delay, self.next_step)

    def do_dls(self):
        if len(self.stk) == 0:
            self.status.config(text="No path in depth limit!", fg='red')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        n, p, d = self.stk.pop()
        self.steps += 1
        
        self.frontier = []
        for node, path, depth in self.stk:
            self.frontier.append(node)
        
        self.draw()
        
        if n == self.target:
            self.path = p
            self.frontier = []
            self.draw()
            self.status.config(text="Found! Depth: " + str(d) + 
                              " Steps: " + str(self.steps), fg='darkgreen')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        if n != self.start:
            self.explored.append(n)
        
        if d < self.depth_lim:
            nbrs = self.get_nbrs(n)
            for nbr in nbrs:
                if nbr not in self.visited:
                    self.visited.add(nbr)
                    new_p = p + [nbr]
                    self.stk.append((nbr, new_p, d + 1))
        
        self.status.config(text="Step " + str(self.steps) + " | Depth: " + 
                          str(d) + " | Limit: " + str(self.depth_lim), fg='blue')
        
        if self.searching:
            self.root.after(self.delay, self.next_step)

    def do_iddfs(self):
        if len(self.stk) == 0:
            if self.depth_lim >= self.max_depth:
                self.status.config(text="No path (max depth)!", fg='red')
                self.start_btn.config(state='normal')
                self.searching = False
                return
            
            #increase depth
            self.depth_lim += 1
            self.stk = []
            self.stk.append((self.start, [self.start], 0))
            self.visited = set()
            self.explored = []
            self.frontier = []
            self.draw()
            self.status.config(text="Increasing depth to " + str(self.depth_lim), fg='orange')
            
            if self.searching:
                self.root.after(self.delay, self.next_step)
            return
        
        n, p, d = self.stk.pop()
        self.steps += 1
        
        self.frontier = []
        for node, path, depth in self.stk:
            self.frontier.append(node)
        
        self.draw()
        
        if n == self.target:
            self.path = p
            self.frontier = []
            self.draw()
            self.status.config(text="Found! Depth: " + str(d) + 
                              " Steps: " + str(self.steps), fg='darkgreen')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        if n != self.start:
            if n not in self.explored:
                self.explored.append(n)
        
        if d < self.depth_lim:
            nbrs = self.get_nbrs(n)
            for nbr in nbrs:
                if nbr not in self.visited:
                    self.visited.add(nbr)
                    new_p = p + [nbr]
                    self.stk.append((nbr, new_p, d + 1))
        
        self.status.config(text="Step " + str(self.steps) + " | Depth: " + 
                          str(d) + "/" + str(self.depth_lim), fg='blue')
        
        if self.searching:
            self.root.after(self.delay, self.next_step)

    def do_bidirectional(self):
        if len(self.fwd_q) == 0 and len(self.bwd_q) == 0:
            self.status.config(text="No path!", fg='red')
            self.start_btn.config(state='normal')
            self.searching = False
            return
        
        self.steps += 1
        
        #alternate fwd/bwd
        if self.steps % 2 == 1 and len(self.fwd_q) > 0:
            curr = self.fwd_q.popleft()
            
            if curr != self.start:
                if curr not in self.explored:
                    self.explored.append(curr)
            
            if curr in self.bwd_visited:
                #found intersection
                p = self.build_path(curr)
                self.path = p
                self.frontier = []
                self.draw()
                self.status.config(text="Found! Length: " + str(len(p)) + 
                                  " Steps: " + str(self.steps), fg='darkgreen')
                self.start_btn.config(state='normal')
                self.searching = False
                return
            
            nbrs = self.get_nbrs(curr)
            for nbr in nbrs:
                if nbr not in self.fwd_visited:
                    self.fwd_visited[nbr] = curr
                    self.fwd_parent[nbr] = curr
                    self.fwd_q.append(nbr)
        
        elif len(self.bwd_q) > 0:
            curr = self.bwd_q.popleft()
            
            if curr != self.target:
                if curr not in self.explored:
                    self.explored.append(curr)
            
            if curr in self.fwd_visited:
                p = self.build_path(curr)
                self.path = p
                self.frontier = []
                self.draw()
                self.status.config(text="Found! Length: " + str(len(p)) + 
                                  " Steps: " + str(self.steps), fg='darkgreen')
                self.start_btn.config(state='normal')
                self.searching = False
                return
            
            nbrs = self.get_nbrs(curr)
            for nbr in nbrs:
                if nbr not in self.bwd_visited:
                    self.bwd_visited[nbr] = curr
                    self.bwd_parent[nbr] = curr
                    self.bwd_q.append(nbr)
        
        self.frontier = []
        for node in self.fwd_q:
            self.frontier.append(node)
        for node in self.bwd_q:
            self.frontier.append(node)
        
        self.draw()
        
        self.status.config(text="Step " + str(self.steps) + " | Fwd: " + 
                          str(len(self.fwd_q)) + " | Bwd: " + 
                          str(len(self.bwd_q)), fg='blue')
        
        if self.searching:
            self.root.after(self.delay, self.next_step)
    
    def build_path(self, meeting):
        #fwd path
        fwd = []
        curr = meeting
        while curr is not None:
            fwd.append(curr)
            curr = self.fwd_parent[curr]
        fwd.reverse()
        
        #bwd path
        bwd = []
        curr = self.bwd_parent[meeting]
        while curr is not None:
            bwd.append(curr)
            curr = self.bwd_parent[curr]
        
        return fwd + bwd

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfinderGUI(root)
    root.mainloop()