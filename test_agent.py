"""Run demo_agent vs random N times and report win rate."""
import sys
import argparse
from kaggle_environments import make
from custom_agents.demo_agent import agent as demo_agent

def run(n, seeds=None):
    wins = draws = losses = 0
    for i in range(n):
        seed = seeds[i] if seeds else i
        env = make("crawl", configuration={"randomSeed": seed})
        env.run([demo_agent, "random"])
        r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
        if r0 > r1:
            wins += 1
        elif r0 == r1:
            draws += 1
        else:
            losses += 1

    print(f"Results over {n} games (vs random):")
    print(f"  Wins:   {wins:3d}  ({100*wins/n:.1f}%)")
    print(f"  Draws:  {draws:3d}  ({100*draws/n:.1f}%)")
    print(f"  Losses: {losses:3d}  ({100*losses/n:.1f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=20, help="number of games")
    args = parser.parse_args()
    run(args.n)
