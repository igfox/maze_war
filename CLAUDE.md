# Maze War

Kaggle [Maze Crawler](https://www.kaggle.com/competitions/maze-crawler) competition. The goal is to build the best agent for the `crawl` simulation environment.

## Competition

- **Environment name**: `"crawl"` (in `kaggle_environments`)
- **Format**: 1v1, infinite scrolling maze with fog of war
- **Submission**: a single `main.py` exposing `agent(obs, config) -> dict`
- **Kaggle username**: ianfox

## Game mechanics

The maze scrolls south every turn — a factory that falls off the bottom loses. Both players start with one factory and build units using energy.

**Unit types** (stored in `obs.robots`, keyed by uid, value is `[type, col, row, energy, player, ...]`):
- `0` = Factory — must keep moving north; can build scouts/workers/miners
- `1` = Scout — fast, collects crystals
- `2` = Worker — can remove walls (`REMOVE_{DIR}`)
- `3` = Miner — place on a mining node and `TRANSFORM` for 50 energy/turn

**Wall encoding**: flat array `obs.walls`, one bitfield per visible cell. Bits: `N=1, E=2, S=4, W=8`. Cell index = `(row - obs.southBound) * config.width + col`.

**Key actions**: `NORTH/SOUTH/EAST/WEST`, `JUMP_NORTH` (factory, 2-cell leap over walls), `BUILD_SCOUT/BUILD_WORKER/BUILD_MINER`, `TRANSFER_{DIR}` (send all energy to adjacent unit), `REMOVE_{DIR}` (worker removes wall), `TRANSFORM` (miner on node), `IDLE`.

## Local development

```bash
pip install -r requirements.txt
python main.py          # runs agent vs "random", prints final rewards
```

## Submitting

Accept competition rules at https://www.kaggle.com/competitions/maze-crawler/rules first, then:

```bash
kaggle competitions submit maze-crawler -f main.py -m "description"
```

## Current agent (`main.py`)

`agent_v2` from bovard's getting-started notebook:
- Factory bug-moves north (prefers `NORTH` → `JUMP_NORTH` → `EAST` → `WEST`)
- Keeps one scout alive (rebuilds on death)
- Scout snail-moves to nearest crystal, transfers energy back when ≥ 75

## Ideas to explore

- Build workers to `REMOVE_NORTH` walls instead of burning the jump cooldown
- Build miners on mining nodes for steady 50 energy/turn income
- Run multiple scouts assigned to different crystals
- Replace snail-move with BFS once walls are cached
