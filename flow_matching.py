"""
Solve one digit at a time (all 1s, then all 2s, …), using a max-flow model to pick non-conflicting spots for that digit.
Between these digit passes, use quick human-style rules (singles) to clean up easy placements. 
Repeat until nothing else changes.

Start with easy wins (naked singles, hidden singles)
Do multiple rounds (to try and place each digit once, then run singles again)
Pick the next digit via fewest candidates first
Build a flow network for one digit (k) (makes a graph node for rows, cols, and boxes that still need k)
Accept partial progress
    Even if the flow can't place all k's, keep whatever it did place then move on
Repeat for all digits, then repeat the whole round. (aka, run singles again...)

Stopping conditions:
    - Stop when a full round makes no changes
    - When you hit a max number of rounds
    - When the board is solved

Principles from class used:
    - Graph modeling 
    - Graph Search
    - Greedy heuristics
    - Iterative improvements
    - Divide and conquer
    - Dynamic-programming (state reuse)
    - Problem reduction
"""

from collections import deque
from typing import List, Tuple, Optional, Set
from copy import deepcopy
from random import shuffle, seed as set_seed, randint

# ----------------------------
# Helper functions
# ----------------------------

def _box_index(n: int, r: int, c: int) -> int:
    return (r // n) * n + (c // n)

def _row_duplicates(vals: List[int]) -> int:
    seen = set()
    dup = 0
    for v in vals:
        if v == 0:
            continue
        if v in seen:
            dup += 1
        else:
            seen.add(v)
    return dup

def _conflict_score(board: List[List[int]], n: int) -> int:
    N = n*n
    score = 0
    for r in range(N):
        score += _row_duplicates(board[r])
    for c in range(N):
        col = [board[r][c] for r in range(N)]
        score += _row_duplicates(col)
    return score

def _legal_digits_for_cell(board: List[List[int]], n: int, r: int, c: int) -> Set[int]:
    """Return the set of digits that can legally go in (r,c) given current board."""
    if board[r][c] != 0:
        return set()
    N = n*n
    used = set(board[r])  # row
    used.update(board[i][c] for i in range(N))  # col
    br = (r // n) * n
    bc = (c // n) * n
    for i in range(br, br + n):
        for j in range(bc, bc + n):
            used.add(board[i][j])
    used.discard(0)
    return {d for d in range(1, N+1) if d not in used}

def _compute_all_candidates(board: List[List[int]], n: int) -> List[List[Set[int]]]:
    N = n*n
    C = [[set() for _ in range(N)] for __ in range(N)]
    for r in range(N):
        for c in range(N):
            C[r][c] = _legal_digits_for_cell(board, n, r, c)
    return C

# ----------------------------
# Max-flow Functions (cap=1)
# ----------------------------

class Dinic:
    def __init__(self, node_count: int):
        self.N = node_count
        self.adj = [[] for _ in range(node_count)]
        self.to = []
        self.cap = []
        self.level = [0]*node_count
        self.it = [0]*node_count

    def _add_edge_internal(self, u: int, v: int, c: int):
        self.adj[u].append(len(self.to))
        self.to.append(v)
        self.cap.append(c)
        self.adj[v].append(len(self.to))
        self.to.append(u)
        self.cap.append(0)

    def add_edge(self, u: int, v: int, c: int = 1):
        self._add_edge_internal(u, v, c)

    def bfs(self, s: int, t: int) -> bool:
        for i in range(self.N):
            self.level[i] = -1
        q = deque([s])
        self.level[s] = 0
        while q:
            u = q.popleft()
            for ei in self.adj[u]:
                v = self.to[ei]
                if self.cap[ei] > 0 and self.level[v] < 0:
                    self.level[v] = self.level[u] + 1
                    q.append(v)
        return self.level[t] >= 0

    def dfs(self, u: int, t: int, f: int) -> int:
        if u == t:
            return f
        i = self.it[u]
        while i < len(self.adj[u]):
            self.it[u] = i
            ei = self.adj[u][i]
            v = self.to[ei]
            if self.cap[ei] > 0 and self.level[v] == self.level[u] + 1:
                pushed = self.dfs(v, t, min(f, self.cap[ei]))
                if pushed:
                    self.cap[ei] -= pushed
                    self.cap[ei ^ 1] += pushed
                    return pushed
            i += 1
        return 0

    def maxflow(self, s: int, t: int) -> int:
        flow = 0
        INF = 10**9
        while self.bfs(s, t):
            for i in range(self.N):
                self.it[i] = 0
            while True:
                pushed = self.dfs(s, t, INF)
                if pushed == 0:
                    break
                flow += pushed
        return flow

# ----------------------------
# Per-digit flow construction
# ----------------------------

def _build_flow_for_digit(board: List[List[int]], n: int, k: int):
    """
    Build a flow network to place digit k. Create nodes for:
      S -> boxes (that still need k) -> row_in -> row_out -> columns (that still need k) -> T
    Add edges for every legal (r,c) spot for k, mapping through its box and row/col nodes.
    Record the R_out->C edges to decode chosen (r,c) after flow.
    """
    N = n*n

    # Track which constraints already satisfied by k
    row_has = [False]*N
    col_has = [False]*N
    box_has = [False]*N
    for r in range(N):
        for c in range(N):
            if board[r][c] == k:
                row_has[r] = True
                col_has[c] = True
                box_has[_box_index(n, r, c)] = True

    # Node mapping
    next_id = 0
    S = next_id; next_id += 1

    box_id = [-1]*N
    for b in range(N):
        if not box_has[b]:
            box_id[b] = next_id
            next_id += 1

    row_in = [-1]*N
    row_out = [-1]*N
    for r in range(N):
        if not row_has[r]:
            row_in[r]  = next_id; next_id += 1
            row_out[r] = next_id; next_id += 1

    col_id = [-1]*N
    for c in range(N):
        if not col_has[c]:
            col_id[c] = next_id
            next_id += 1

    T = next_id; next_id += 1

    din = Dinic(next_id)

    # Capacities
    for b in range(N):
        if box_id[b] != -1:
            din.add_edge(S, box_id[b], 1)
    for r in range(N):
        if row_in[r] != -1:
            din.add_edge(row_in[r], row_out[r], 1)
    for c in range(N):
        if col_id[c] != -1:
            din.add_edge(col_id[c], T, 1)

    # Legal placement edges
    decode_edges: List[Tuple[int,int,int]] = []  # (edge_idx, r, c)

    def legal_cell_for_k(r: int, c: int) -> bool:
        if board[r][c] != 0:
            return False
        # quick legality check via row/col/box
        if any(board[r][cc] == k for cc in range(N)):
            return False
        if any(board[rr][c] == k for rr in range(N)):
            return False
        br = (r // n) * n
        bc = (c // n) * n
        for rr in range(br, br + n):
            for cc in range(bc, bc + n):
                if board[rr][cc] == k:
                    return False
        return True

    for r in range(N):
        for c in range(N):
            if not legal_cell_for_k(r, c):
                continue
            b = _box_index(n, r, c)
            if box_id[b] == -1 or row_in[r] == -1 or col_id[c] == -1:
                continue
            din.add_edge(box_id[b], row_in[r], 1)
            before_len = len(din.to)
            din.add_edge(row_out[r], col_id[c], 1)
            decode_edges.append((before_len, r, c))

    # Target is the theoretical count still needed; but does NOT require hitting it. (partial acceptance bby)
    need_boxes = sum(1 for b in range(N) if not box_has[b])
    need_rows  = sum(1 for r in range(N) if not row_has[r])
    need_cols  = sum(1 for c in range(N) if not col_has[c])
    target = min(need_boxes, need_rows, need_cols)

    return din, S, T, decode_edges, target

def _extract_flow_placements(din: Dinic, decode_edges: List[Tuple[int,int,int]]) -> List[Tuple[int,int]]:
    """If forward cap on an R_out->C edge is 0 after maxflow, that (r,c) was chosen."""
    res = []
    for edge_idx, r, c in decode_edges:
        if din.cap[edge_idx] == 0:
            res.append((r, c))
    return res

# ----------------------------
# Constraint propagation (singles)
# ----------------------------

def _apply_naked_singles(board: List[List[int]], n: int) -> int:
    """Fill cells that have only one legal digit. Returns number of assignments made."""
    N = n*n
    count = 0
    C = _compute_all_candidates(board, n)
    changed = True
    while changed:
        changed = False
        for r in range(N):
            for c in range(N):
                if board[r][c] == 0 and len(C[r][c]) == 1:
                    d = next(iter(C[r][c]))
                    board[r][c] = d
                    count += 1
                    # Update local neighborhood cheaply
                    C = _compute_all_candidates(board, n)
                    changed = True
    return count

def _apply_hidden_singles(board: List[List[int]], n: int) -> int:
    """If a digit appears as a candidate in exactly one cell of a unit (row/col/box), place it."""
    N = n*n
    placed = 0
    C = _compute_all_candidates(board, n)

    # Rows
    for r in range(N):
        pos = [set() for _ in range(N+1)]
        for c in range(N):
            for d in C[r][c]:
                pos[d].add((r, c))
        for d in range(1, N+1):
            if len(pos[d]) == 1:
                (rr, cc) = next(iter(pos[d]))
                if board[rr][cc] == 0:
                    board[rr][cc] = d
                    placed += 1
                    C = _compute_all_candidates(board, n)

    # Cols
    for c in range(N):
        pos = [set() for _ in range(N+1)]
        for r in range(N):
            for d in C[r][c]:
                pos[d].add((r, c))
        for d in range(1, N+1):
            if len(pos[d]) == 1:
                (rr, cc) = next(iter(pos[d]))
                if board[rr][cc] == 0:
                    board[rr][cc] = d
                    placed += 1
                    C = _compute_all_candidates(board, n)

    # Boxes
    for br in range(0, N, n):
        for bc in range(0, N, n):
            pos = [set() for _ in range(N+1)]
            cells = [(r, c) for r in range(br, br+n) for c in range(bc, bc+n)]
            for (r, c) in cells:
                for d in C[r][c]:
                    pos[d].add((r, c))
            for d in range(1, N+1):
                if len(pos[d]) == 1:
                    (rr, cc) = next(iter(pos[d]))
                    if board[rr][cc] == 0:
                        board[rr][cc] = d
                        placed += 1
                        C = _compute_all_candidates(board, n)
    return placed

def _propagate(board: List[List[int]], n: int) -> int:
    """Run singles until stuck. Returns number of assignments made."""
    total = 0
    while True:
        a = _apply_naked_singles(board, n)
        b = _apply_hidden_singles(board, n)
        total += a + b
        if a + b == 0:
            return total

# ----------------------------
# Main algorithms
# ----------------------------

def _digit_candidate_count(board: List[List[int]], n: int, k: int) -> int:
    N = n*n
    cnt = 0
    for r in range(N):
        for c in range(N):
            if board[r][c] == 0 and k in _legal_digits_for_cell(board, n, r, c):
                cnt += 1
    return cnt

def flow_matching_sudoku(board: List[List[int]], n: int, *, restarts: int = 5, seed: Optional[int] = None,
                         max_rounds: int = 20) -> List[List[int]]:
    """
    Per-digit Max-Flow solver with iterative rounds and constraint propagation.
    - Accepts partial flows; iterates digits in greedy order.
    - Runs singles between passes to clean up Easy/Medium cases.
    """
    if seed is not None:
        set_seed(seed)

    N = n*n
    best_board = None
    best_score = None
    base = deepcopy(board)

    for attempt in range(restarts):
        cur = deepcopy(base)

        # Initial propagation (often places a lot on easy boards)
        _propagate(cur, n)

        progressed = True
        rounds = 0
        while progressed and rounds < max_rounds:
            progressed = False
            rounds += 1

            # Greedy digit order (fewest candidates first)
            digits = list(range(1, N+1))
            digits.sort(key=lambda k: _digit_candidate_count(cur, n, k))
            if seed is None:
                # light tie-breaking shuffle
                for _ in range(3):
                    i = randint(0, N-2)
                    if randint(0, 1):
                        digits[i], digits[i+1] = digits[i+1], digits[i]

            for k in digits:
                # Build & run flow
                din, S, T, decode_edges, _target = _build_flow_for_digit(cur, n, k)
                if not decode_edges:
                    continue
                f = din.maxflow(S, T)
                if f > 0:
                    placements = _extract_flow_placements(din, decode_edges)
                    for (r, c) in placements:
                        if cur[r][c] == 0:  # safety
                            cur[r][c] = k
                            progressed = True

                    # After placing some ks, propagate constraints
                    if _propagate(cur, n) > 0:
                        progressed = True

            # End of one global round: try a final propagation
            if _propagate(cur, n) > 0:
                progressed = True

        score = _conflict_score(cur, n)
        if best_score is None or score < best_score:
            best_score = score
            best_board = cur

        if best_score == 0:
            break

    return best_board
