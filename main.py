from board import Board
from trainer import Trainer # type: ignore

def main():
    arena = Trainer()

    challenger_config = {
        "use_quiescence": True,
        "use_singular_extension": True,
        "use_probcut": True,
        "use_iterative_deepening": True
    }


    baseline_config = {
        "use_quiescence": False,
        "use_singular_extension": False,
        "use_probcut": False,
        "use_iterative_deepening": False
    }

    print("Starting Connect 4 Engine Match")
    print("-" * 40)

    num_games = 10
    arena.play_match(
        p1_settings =challenger_config,
        p2_settings =baseline_config,
        games=num_games,
        p1_depth=6, 
        p2_depth=6
    )

    print("-" * 40)
    print("FINAL RESULTS")
    print(f"Challenger Wins: {arena.stats['challenger_wins']}")
    print(f"Baseline Wins:   {arena.stats['baseline_wins']}")
    print(f"Draws:           {arena.stats['draws']}")
    
    total_nodes = arena.stats.get("total_nodes", 0)
    print(f"Total Nodes Processed: {total_nodes:,}")
    print("-" * 40)

if __name__ == "__main__":
    main()