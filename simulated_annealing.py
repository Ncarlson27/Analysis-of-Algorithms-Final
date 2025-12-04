import math
from copy import deepcopy
from random import randint, shuffle, random, sample, seed as set_seed

# ----------------------------
# Helper functions here
# ----------------------------

def _validate_clues(board: list, n: int) -> bool:
    """Returns true if no box has duplicate nonzero clues. 
       Otherwise, it's invalid and returns false. """
    N = n * n
    for br in range(0, N, n):
        for bc in range(0, N, n):
            seen = set()
            for r in range(br, br + n):
                for c in range(bc, bc + n):
                    v = board[r][c]
                    if v != 0:
                        if v in seen:
                            return False
                        seen.add(v)
    return True


def _fill_missing(board: list, n: int) -> list:
    """
    Fill each n*n box with the numbers missing from that box (uniformly shuffled).
    This ensures all box constraints are satisfied from the start.
    """
    N = n * n
    state = [row[:] for row in board]  # copy
    for br in range(0, N, n):
        for bc in range(0, N, n):
            present = set()
            empties = []
            for r in range(br, br + n):
                for c in range(bc, bc + n):
                    v = state[r][c]
                    if v == 0:
                        empties.append((r, c))
                    else:
                        present.add(v)
            missing = [d for d in range(1, N + 1) if d not in present]
            shuffle(missing)
            # Fisher-Yates style shuffle via random sampling of pairs below; order doesn't matter
            for (r, c), d in zip(empties, missing):
                state[r][c] = d
    return state


def _row_duplicates(vals: list[int]) -> int:
    """Return the number of duplicates in a row/column. 
       If all numbers are unique, then it'll return 0."""
    
    # Faster than Counter for small fixed sizes
    seen = set()
    dup = 0
    for v in vals:
        if v in seen:
            dup += 1
        else:
            seen.add(v)
    return dup


def _calculate_cost(board: list, n: int) -> int:
    """Total num of conflicts = duplicates across all rows and columns."""
    N = n * n
    conflicts = 0
    for r in range(N):
        conflicts += _row_duplicates(board[r])
    for c in range(N):
        col = [board[r][c] for r in range(N)]
        conflicts += _row_duplicates(col)
    return conflicts


def _delta_cost_after_swap(state: list, n: int, r1: int, c1: int, r2: int, c2: int) -> int:
    """
    Computes the cost change if we swap (r1,c1) <-> (r2,c2).
    Note to self: Only rows r1,r2 and cols c1,c2 can change!!
    """
    N = n * n

    def row_cost(r):
        return _row_duplicates(state[r])

    def col_cost(c):
        return _row_duplicates([state[r][c] for r in range(N)])

    before = row_cost(r1) + row_cost(r2) + col_cost(c1) + col_cost(c2)

    # do swap
    state[r1][c1], state[r2][c2] = state[r2][c2], state[r1][c1]
    after = row_cost(r1) + row_cost(r2) + col_cost(c1) + col_cost(c2)
    # swap back
    state[r1][c1], state[r2][c2] = state[r2][c2], state[r1][c1]

    return after - before


def _conflicted_rows_cols(board: list, n: int):
    """Returns the sets of row indices and column indices that currently have conflicts."""
    N = n * n
    bad_rows, bad_cols = set(), set()
    for r in range(N):
        if _row_duplicates(board[r]) > 0:
            bad_rows.add(r)
    for c in range(N):
        col = [board[r][c] for r in range(N)]
        if _row_duplicates(col) > 0:
            bad_cols.add(c)
    return bad_rows, bad_cols


def _pick_conflicted_box(n: int, bad_rows: set[int], bad_cols: set[int]) -> tuple[int, int]:
    """
    Chooses which n*n box to target for a swap during simulated annealing.
    Returns (box_row_index, box_col_index) in [0..n-1]^2 for identifying the 
    chosen box within the grid.
    """
    N = n * n
    candidates = set()
    if bad_rows or bad_cols:
        rows = bad_rows if bad_rows else set(range(N))
        cols = bad_cols if bad_cols else set(range(N))
        for r in rows:
            for c in cols:
                candidates.add((r // n, c // n))
    else:
        # no detected conflicts; choose randomly
        return randint(0, n - 1), randint(0, n - 1)

    brbc = list(candidates)
    i = randint(0, len(brbc) - 1)
    return brbc[i]


def _swap_random_in_box(state: list, clues: set[tuple[int, int]], n: int, choose_box_from_conflicts=True) -> tuple[list, tuple|None]:
    """
    Swaps two non-clue cells within a chosen box to keep box validity.
    Returns (new_state, (r1,c1,r2,c2)) or (state, None) if there was no swap possible.
    """
    N = n * n
    if choose_box_from_conflicts:
        bad_r, bad_c = _conflicted_rows_cols(state, n)
        br, bc = _pick_conflicted_box(n, bad_r, bad_c)
    else:
        br, bc = randint(0, n - 1), randint(0, n - 1)

    free = [(r, c)
            for r in range(br * n, br * n + n)
            for c in range(bc * n, bc * n + n)
            if (r, c) not in clues]

    if len(free) < 2:
        return state, None

    (r1, c1), (r2, c2) = sample(free, 2)
    new_state = [row[:] for row in state]
    new_state[r1][c1], new_state[r2][c2] = new_state[r2][c2], new_state[r1][c1]
    return new_state, (r1, c1, r2, c2)


def _schedule_defaults(n: int) -> tuple[float, float, float, int]:
    """
    Polynomial schedule tied to size:
    iterations_per_temp ~ O((n^2)^2) = O(n^4) (81*50 ~ 4050 for 9x9).
    """
    N = n * n
    T0 = 1.0
    Tmin = 1e-4
    alpha = 0.995
    iterations_per_temp = 50 * N
    return T0, Tmin, alpha, iterations_per_temp

# ----------------------------
# The main SA work is here
# ----------------------------

def _run_single_sa(board: list, n: int, *, 
                   T0: float = None,
                   Tmin: float = None,
                   alpha: float = None,
                   iterations_per_temp: int = None,
                   patience: int = 5000,
                   seed: int | None = None,
                   use_delta: bool = True) -> list:
    """
    Run a single SA trajectory and return the best board found from that run.
    """
    if seed is not None:
        set_seed(seed)

    assert _validate_clues(board, n), "Invalid puzzle: duplicate clues inside a box."

    if T0 is None or Tmin is None or alpha is None or iterations_per_temp is None:
        dT0, dTmin, dalpha, diter = _schedule_defaults(n)
        T0 = dT0 if T0 is None else T0
        Tmin = dTmin if Tmin is None else Tmin
        alpha = dalpha if alpha is None else alpha
        iterations_per_temp = diter if iterations_per_temp is None else iterations_per_temp

    N = n * n
    clues = {(r, c) for r in range(N) for c in range(N) if board[r][c] != 0}

    state = _fill_missing(board, n)
    current_cost = _calculate_cost(state, n)

    best_state = [row[:] for row in state]
    best_cost = current_cost

    T = T0
    no_improve = 0

    # Early exit if already solved
    if best_cost == 0:
        return best_state

    while T > Tmin:
        for _ in range(iterations_per_temp):
            # propose a move (preserving box validity)
            proposal, coords = _swap_random_in_box(state, clues, n, choose_box_from_conflicts=True)
            if coords is None:
                # no swap possible in that box; try another iteration
                continue

            if use_delta:
                r1, c1, r2, c2 = coords
                delta = _delta_cost_after_swap(state, n, r1, c1, r2, c2)
                new_cost = current_cost + delta
            else:
                new_cost = _calculate_cost(proposal, n)

            diff = new_cost - current_cost
            accept = diff <= 0 or random() < math.exp(-diff / T)

            if accept:
                state = proposal
                current_cost = new_cost
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_state = [row[:] for row in state]
                    no_improve = 0
                else:
                    no_improve += 1
            else:
                no_improve += 1

            if best_cost == 0 or no_improve >= patience:
                return best_state

        T *= alpha

    return best_state


# ----------------------------
# Public API used in main.py
# ----------------------------

def simulated_annealing(board: list, n: int, *, restarts: int = 1, seed: int | None = None, **kwargs) -> list:
    """
    SA wrapper expected by main.py:
      - returns a BOARD (not stats)
      - supports multiple restarts and optional seeding
      - kwargs pass through to _run_single_sa (T0, Tmin, alpha, iterations_per_temp, patience, use_delta)
    """
    best_board = None
    best_cost = None

    # Split seed across restarts deterministically if provided
    for r in range(restarts):
        rseed = None if seed is None else (seed + r)
        candidate = _run_single_sa(board, n, seed=rseed, **kwargs)
        cost = _calculate_cost(candidate, n)
        if best_board is None or cost < best_cost:
            best_board = candidate
            best_cost = cost
        if best_cost == 0:
            break

    return best_board
