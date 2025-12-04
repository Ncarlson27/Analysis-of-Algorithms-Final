import numpy as np
from typing import Tuple, List, Optional
from random import seed as set_seed, randint

# ----------------------------
# Helpers & validation functions
# ----------------------------

def _one_hot(value: int, n: int) -> np.ndarray:
    """Return one-hot vector of length n^2 for a clue with a value between 1 and n^2."""
    vec = np.zeros(n**2, dtype=float)
    vec[value - 1] = 1.0
    return vec


def _normalize(vec: np.ndarray) -> np.ndarray:
    """Returns vec with scaled sum to 1 (as long as sum is greater than 0), 
    otherwise it returns vec unchanged."""
    s = vec.sum()
    return vec / s if s > 0 else vec


def _validate_clues(clues: np.ndarray, n: int) -> bool:
    """ This checks within each n by n box for duplicate nonzero clues."""
    N = n * n
    for br in range(0, N, n):
        for bc in range(0, N, n):
            seen = set()
            for r in range(br, br + n):
                for c in range(bc, bc + n):
                    v = int(clues[r, c])
                    if v != 0:
                        if v in seen:
                            return False
                        seen.add(v)
    return True


def initialize_weights(clues: List[List[int]], n: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build weight array W of shape (N, N, N), where W[r,c,k] is weight that cell (r,c) = k+1.
    If clues[r][c] != 0 then we do a one-hot at that value, otherwise it's uniform.
    Returns (weights, clues_arr).
    """
    clues_arr = np.array(clues, dtype=int)
    assert clues_arr.shape[0] == clues_arr.shape[1], "Clue grid must be square."
    N = n * n
    W = np.zeros((N, N, N), dtype=float)

    for r in range(N):
        for c in range(N):
            v = clues_arr[r, c]
            if v == 0:
                W[r, c, :] = 1.0 / N
            else:
                W[r, c, :] = _one_hot(v, n)

    return W, clues_arr

# ----------------------------
# Projection functions
# ----------------------------

def project_cells(W: np.ndarray, clues: np.ndarray, n: int) -> None:
    """
    Per-cell projection: for blanks, normalize the length-N vector;
    for clues, re-do one-hot.
    """
    N = n * n
    for r in range(N):
        for c in range(N):
            v = int(clues[r, c])
            if v == 0:
                W[r, c, :] = _normalize(W[r, c, :])
            else:
                W[r, c, :] = _one_hot(v, n)


def project_rows(W: np.ndarray, clues: np.ndarray, n: int) -> None:
    """
    For each row r and number k:
      - If row r already has a clue with value (k+1), force W[r, that_c, k]=1 and W[r, c!=that_c, k]=0.
      - Else, zero out clue positions for that k and normalize over remaining columns.
    """
    N = n * n
    for r in range(N):
        for k in range(N):  # number = k+1
            # Find columns with a clue equal to (k+1)
            clue_cols = [c for c in range(N) if int(clues[r, c]) == (k + 1)]
            if len(clue_cols) > 0:
                # If invalid puzzle has multiple such clues, still force one-hot on all of them (rare; validation should catch)
                # Here, we enforce they soak up all mass for this k in this row.
                mask = np.zeros(N, dtype=float)
                for c in clue_cols:
                    mask[c] = 1.0
                # If there are multiple, normalize equally among them (defensive)
                mask = _normalize(mask)
                W[r, :, k] = mask
            else:
                # Zero out clue columns for this k; keep only non-clue columns
                vec = W[r, :, k].copy()
                for c in range(N):
                    if int(clues[r, c]) != 0:
                        vec[c] = 0.0
                W[r, :, k] = _normalize(vec)


def project_columns(W: np.ndarray, clues: np.ndarray, n: int) -> None:
    """
    For each column c and number k:
      - If column c has a clue (k+1), force that row’s k-weight to 1 and others 0.
      - Else, zero out clue rows for that k and normalize over remaining rows.
    """
    N = n * n
    for c in range(N):
        for k in range(N):  # number = k+1
            clue_rows = [r for r in range(N) if int(clues[r, c]) == (k + 1)]
            if len(clue_rows) > 0:
                mask = np.zeros(N, dtype=float)
                for r in clue_rows:
                    mask[r] = 1.0
                mask = _normalize(mask)
                W[:, c, k] = mask
            else:
                vec = W[:, c, k].copy()
                for r in range(N):
                    if int(clues[r, c]) != 0:
                        vec[r] = 0.0
                W[:, c, k] = _normalize(vec)


def project_boxes(W: np.ndarray, clues: np.ndarray, n: int) -> None:
    """
    For each n*n box and number k:
      - If the box contains a clue (k+1), force that cell's k-weight to 1 and others 0 (within the box).
      - Else, zero out clue cells in the box for k and normalize over the free cells of the box.
    """
    N = n * n
    for br in range(0, N, n):
        for bc in range(0, N, n):
            rows = range(br, br + n)
            cols = range(bc, bc + n)
            for k in range(N):  # number = k+1
                # Gather coords in the box
                coords = [(r, c) for r in rows for c in cols]
                clue_cells = [(r, c) for (r, c) in coords if int(clues[r, c]) == (k + 1)]
                if len(clue_cells) > 0:
                    # Force mass to the clue cell(s) for k
                    mask = np.zeros((n, n), dtype=float)
                    for (r, c) in clue_cells:
                        mask[r - br, c - bc] = 1.0
                    # If multiple (invalid), normalize among them to be safe
                    mask /= mask.sum()
                    # Write back to W
                    for idx, (r, c) in enumerate(coords):
                        W[r, c, k] = mask[(r - br), (c - bc)]
                else:
                    # Zero out clue positions for k, normalize over remaining in the box
                    vec = []
                    for (r, c) in coords:
                        v = 0.0 if int(clues[r, c]) != 0 else W[r, c, k]
                        vec.append(v)
                    vec = np.array(vec, dtype=float)
                    vec = _normalize(vec)
                    for idx, (r, c) in enumerate(coords):
                        W[r, c, k] = vec[idx]

# ----------------------------
# Convergence & scoring utils
# ----------------------------

def _max_change(W: np.ndarray, W_old: np.ndarray) -> float:
    """ Computes a single scalar that measures how much the weights tensor 
        changed in the last iteration. """
    return np.max(np.abs(W - W_old))


def _conflict_score(board: np.ndarray, n: int) -> int:
    """Counts duplicates in each row and column."""
    N = n * n
    def dup_count(arr):
        seen = set()
        dup = 0
        for v in arr:
            if v in seen:
                dup += 1
            else:
                seen.add(v)
        return dup

    score = 0
    for r in range(N):
        score += dup_count(list(board[r, :]))
    for c in range(N):
        score += dup_count(list(board[:, c]))
    return score

# ----------------------------
# Public API used in main.py
# ----------------------------

def alternating_projections( clues: List[List[int]], n: int, max_iters: int = 500, 
            eps: float = 1e-5, restarts: int = 1, seed: Optional[int] = None) -> List[List[int]]:
    """
    Alternating projections for Sudoku:
      - Maintain W[r,c,k] = weight that cell (r,c) is k+1.
      - Project onto: per-cell simplex, row "one-of-each-number", column "one-of-each-number",
        and box "one-of-each-number", all while respecting clues.
      - Iterate until stable or max_iters, optionally with multiple restarts.
      - Return the best (lowest-conflict) argmax solution across restarts.

    Returns: board as list-of-lists of ints.
    """
    if seed is not None:
        set_seed(seed)
        np.random.seed(seed)

    clues_arr = np.array(clues, dtype=int)
    assert _validate_clues(clues_arr, n), "Invalid puzzle: duplicate clues inside a box."
    N = n * n

    best_board = None
    best_score = None

    for rtry in range(restarts):
        # Randomize start for blanks by small noise around uniform to break ties
        W, clues_arr = initialize_weights(clues, n)
        # Tiny jitter for blanks
        noise = 1e-3 * np.random.rand(N, N, N)
        for r in range(N):
            for c in range(N):
                if clues_arr[r, c] == 0:
                    W[r, c, :] = _normalize(W[r, c, :] + noise[r, c, :])
                else:
                    W[r, c, :] = _one_hot(int(clues_arr[r, c]), n)

        for _ in range(max_iters):
            W_old = W.copy()

            # Project onto each constraint set
            project_cells(W, clues_arr, n)
            project_rows(W, clues_arr, n)
            project_columns(W, clues_arr, n)
            project_boxes(W, clues_arr, n)

            if _max_change(W, W_old) < eps:
                break

        # Build solution: argmax per cell, then reapply clues
        sol = np.argmax(W, axis=2) + 1  # shape (N,N)
        # Force clues (safety)
        for r in range(N):
            for c in range(N):
                v = int(clues_arr[r, c])
                if v != 0:
                    sol[r, c] = v

        score = _conflict_score(sol, n)
        if (best_score is None) or (score < best_score):
            best_score = score
            best_board = sol.copy()

        # Small randomness between restarts
        if seed is None:
            # change RNG state mildly
            _ = randint(0, 1 << 30)

    return best_board.astype(int).tolist()
