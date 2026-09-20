from mcp.server.fastmcp import FastMCP
from ddgs import DDGS
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.vector_store import get_collection


mcp = FastMCP("smartroute-tools")



@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    last_error = None
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            results = DDGS().text(query, max_results = max_results)
            if results:
                break
        except Exception as e:
            last_error = e
            results = None

        if attempt < attempts:
            time.sleep(3)
    else:
        results = None
           

    if not results:
        error_detail = f" ({type(last_error).__name__}: {last_error})" if last_error else ""
        return f"Search failed after {attempts} attempts{error_detail}"

    formatted = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        body = r.get("body", "")
        url = r.get("href", "")
        formatted.append(f"{i}. {title}\n   {body}\n   Source: {url}")

    return "\n\n". join(formatted)

@mcp.tool()
def execute_python(code: str, timeout_seconds: int = 5) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        if not output.strip():
            output = "(no output)"

        return output[:4000]

    except subprocess.TimeoutExpired:
        return f"Execution timed out after {timeout_seconds} seconds"
    except Exception as e:
        return f"Execution failed: {type(e).__name__}: {e}"
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass

@mcp.tool()
def rag_search(query: str, n_results: int = 3) -> str:
    collection = get_collection()

    if collection.count() == 0:
        return "No researcher notes stored yet."

    n = min(n_results, collection.count())
    result = collection.query(query_texts=[query], n_results=n)

    if not result["documents"] or not result["documents"][0]:
        return "No matches found."

    formatted = []
    for i, (doc, meta, dist) in enumerate(
        zip(result["documents"][0], result["metadatas"][0], result["distances"][0]), 1
    ):
        snippet = doc[:300] + ("..." if len(doc) > 300 else "")
        formatted.append(
            f"{i}. Topic: {meta.get('topic')} (distance={round(dist, 4)})\n   {snippet}"
        )
    return "\n\n".join(formatted)

 
if __name__ == "__main__":
    mcp.run()
