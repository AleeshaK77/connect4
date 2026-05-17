from board import Board
from search import Search # type: ignore
import time

def test_singular_extension():
    """
    Test if the AI can 'see' further than its depth limit 
    when forced moves (threats) are involved.
    """
    print("\n--- TEST: SINGULAR EXTENSION (Forced Sequence) ---")
    board = Board()
    
    # We setup a scenario where Player 0 (X) can create a vertical threat
    # that leads to a win, but it takes more plies than the depth limit.
    # X: 3, O: 0, X: 3, O: 0, X: 3...
    moves = [3, 0, 3, 0, 3] 
    for m in moves:
        board.make_move(m)
        
    search = Search(board)
    
    # We set a very low depth where it NORMALLY wouldn't see the end of the game
    test_depth = 2
    
    # 1. Test WITHOUT Singular Extension
    search.settings["use_singular_extension"] = False
    search.settings["use_quiescence"] = False # Keep it pure
    move_no_ext, nodes_no_ext = search.get_best_move(depth_limit=test_depth)
    
    # 2. Test WITH Singular Extension
    search.settings["use_singular_extension"] = True
    move_ext, nodes_ext = search.get_best_move(depth_limit=test_depth)
    
    print(f"Depth Limit: {test_depth}")
    print(f"Move WITHOUT Extension: {move_no_ext} (Nodes: {nodes_no_ext})")
    print(f"Move WITH Extension:    {move_ext} (Nodes: {nodes_ext})")
    
    if nodes_ext > nodes_no_ext:
        print("✅ SUCCESS: Singular Extension expanded the search tree.")
        if move_ext == 3:
            print("✅ SUCCESS: The AI prioritized blocking/completing the threat.")
    else:
        print("⚠️ NOTE: Node counts were similar. The position might not have triggered an extension.")

def test_node_explosion_check():
    """Verify how much the new logic impacts performance."""
    print("\n--- TEST: NODE IMPACT ANALYSIS ---")
    board = Board()
    search = Search(board)
    
    depth = 5
    
    # Baseline: Simple Alpha-Beta
    search.settings["use_quiescence"] = False
    search.settings["use_singular_extension"] = False
    _, n1 = search.get_best_move(depth_limit=depth)
    
    # Full Suite: Quiescence + Extensions
    search.settings["use_quiescence"] = True
    search.settings["use_singular_extension"] = True
    _, n2 = search.get_best_move(depth_limit=depth)
    
    print(f"Nodes @ Depth {depth} (Basic): {n1}")
    print(f"Nodes @ Depth {depth} (Full):  {n2}")
    print(f"Expansion Factor: {n2/n1:.2f}x")

if __name__ == "__main__":
    test_singular_extension()
    test_node_explosion_check()