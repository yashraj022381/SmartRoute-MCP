from mcp_server.client import web_search

if __name__ == "__main__":
    print("Testing web search directly...\n")
    result = web_search("why is the ocean salty", max_results=3)
    print("--- RAW RESULT ---")
    print(result)
