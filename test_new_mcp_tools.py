from mcp_server.client import execute_python, rag_search
 
print("=" * 70)
print("Testing execute_python")
print("-" * 70)
 
print("\n[1] Basic output:")
print(execute_python("print(2 + 2)"))
 
print("\n[2] Multi-line with a loop:")
print(execute_python("total = sum(range(10))\nprint(f'Sum 0-9: {total}')"))
 
print("\n[3] An error (should show [stderr], not crash):")
print(execute_python("print(1 / 0)"))
 
print("\n[4] Infinite loop (should time out cleanly):")
print(execute_python("while True: pass", timeout_seconds=2))
 
print("\n" + "=" * 70)
print("Testing rag_search")
print("-" * 70)
print(rag_search("home composting", n_results=2))
