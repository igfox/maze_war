"""
Demo agent — starting point for development.

Strategy:
- Factory: bug-move north (NORTH > JUMP_NORTH > EAST > WEST)
- Scouts: snail-move to nearest crystal, transfer energy back when full
- Factory rebuilds scouts on death (keeps one alive)
"""

DIRS = {"NORTH": (0, 1), "SOUTH": (0, -1), "EAST": (1, 0), "WEST": (-1, 0)}
WALL_BIT = {"NORTH": 1, "EAST": 2, "SOUTH": 4, "WEST": 8}

print("v1.1")
# --- Helpers -----------------------------------------------------------------

def wall_at(obs, config, col, row):
    idx = (row - obs.southBound) * config.width + col
    if 0 <= idx < len(obs.walls) and obs.walls[idx] != -1:
        return obs.walls[idx]
    return 0


def has_road(obs, config, col, row, direction):
    return not (wall_at(obs, config, col, row) & WALL_BIT[direction])


def neighbor(col, row, direction):
    dc, dr = DIRS[direction]
    return col + dc, row + dr


def my_robots(obs):
    return {uid: data for uid, data in obs.robots.items() if data[4] == obs.player}


def my_factory(obs):
    for uid, data in my_robots(obs).items():
        if data[0] == 0:
            return uid, data
    return None, None


def parse_cell(key):
    c, r = key.split(",")
    return int(c), int(r)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# --- Movement ----------------------------------------------------------------

def factory_bug_north(col, row, jump_cd, obs, config):
    if has_road(obs, config, col, row, "NORTH"):
        return "NORTH"
    if jump_cd == 0:
        return "JUMP_NORTH"
    if has_road(obs, config, col, row, "EAST"):
        return "EAST"
    if has_road(obs, config, col, row, "WEST"):
        return "WEST"
    return "IDLE"


_scout_state = {}  # uid -> {"target": (col, row), "tabu": [(col, row)]}


def snail_step(uid, col, row, target, obs, config):
    """Greedy step toward target, avoiding the last 2 visited cells."""
    state = _scout_state.setdefault(uid, {"target": None, "tabu": []})
    if state["target"] != target:
        state["target"] = target
        state["tabu"] = []

    tc, tr = target
    candidates = []
    for d in ("NORTH", "SOUTH", "EAST", "WEST"):
        if not has_road(obs, config, col, row, d):
            continue
        nc, nr = neighbor(col, row, d)
        if (nc, nr) in state["tabu"]:
            continue
        candidates.append((manhattan((nc, nr), (tc, tr)), d))

    if not candidates:
        state["tabu"] = []
        return "IDLE"

    candidates.sort()
    action = candidates[0][1]
    state["tabu"] = (state["tabu"] + [(col, row)])[-2:]
    return action


# --- Unit policies -----------------------------------------------------------

SCOUT_TRANSFER_ENERGY = 75


def factory_action(uid, col, row, energy, jump_cd, build_cd, scout_count, worker_count, obs, config):
    # Jump immediately if north is blocked — don't sidestep
    if not has_road(obs, config, col, row, "NORTH"):
        return "JUMP_NORTH"
    # Build support units when idle
    if build_cd == 0:
        if worker_count == 0 and energy >= config.workerCost:
            return "BUILD_WORKER"
        if scout_count == 0 and energy >= config.scoutCost:
            return "BUILD_SCOUT"
    return "NORTH"


def worker_action(col, row, energy, obs, config):
    if not has_road(obs, config, col, row, "NORTH") and energy >= config.wallRemoveCost:
        return "REMOVE_NORTH"
    if has_road(obs, config, col, row, "NORTH"):
        return "NORTH"
    if has_road(obs, config, col, row, "EAST"):
        return "EAST"
    if has_road(obs, config, col, row, "WEST"):
        return "WEST"
    return "IDLE"


def scout_action(uid, col, row, energy, factory_pos, obs, config):
    fc, fr = factory_pos

    if energy >= SCOUT_TRANSFER_ENERGY:
        for d in ("NORTH", "SOUTH", "EAST", "WEST"):
            if neighbor(col, row, d) == (fc, fr) and has_road(obs, config, col, row, d):
                return f"TRANSFER_{d}"
        return snail_step(uid, col, row, (fc, fr), obs, config)

    crystals = [parse_cell(k) for k in obs.crystals]
    if crystals:
        target = min(crystals, key=lambda c: manhattan(c, (col, row)))
    else:
        target = (col, row + 5)
    return snail_step(uid, col, row, target, obs, config)


# --- Entry point -------------------------------------------------------------

def agent(obs, config):
    actions = {}
    robots = my_robots(obs)
    _, f_data = my_factory(obs)
    scout_count = sum(1 for d in robots.values() if d[0] == 1)
    worker_count = sum(1 for d in robots.values() if d[0] == 2)

    for uid, data in robots.items():
        rtype, col, row, energy = data[0], data[1], data[2], data[3]
        jump_cd = data[6] if len(data) > 6 else 0
        build_cd = data[7] if len(data) > 7 else 0

        if rtype == 0:
            actions[uid] = factory_action(uid, col, row, energy, jump_cd, build_cd, scout_count, worker_count, obs, config)
        elif rtype == 2:
            actions[uid] = worker_action(col, row, energy, obs, config)
        elif rtype == 1 and f_data is not None:
            factory_pos = (f_data[1], f_data[2])
            actions[uid] = scout_action(uid, col, row, energy, factory_pos, obs, config)

    return actions
