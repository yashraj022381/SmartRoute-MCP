import os
import streamlit as st
import requests

#API_URL = "http://localhost:8000"
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="SmartRoute-MCP", page_icon="🧭", layout="wide")

st.title("🧭 SmartRoute-MCP")
st.caption("A cost-optimized, multi-agent AI system with live routing visibility.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None
    
# --- Sidebar: live stats from the database ---
with st.sidebar:
    st.header("📊 Performance Summary")
    try:
        stats = requests.get(f"{API_URL}/stats", timeout=5).json()
        if stats.get("total_queries", 0) == 0:
            st.info("No data yet. Run something below!")

        else:
            st.metric("Total queries routed", stats["total_queries"])
            st.metric("Total estimated cost", f"${stats['total_cost_usd']:.6f}")
            st.metric("Fallback rate", f"{stats['fallback_rate'] * 100:.1f}%")
            st.write("**Split by tier:**")
            st.json(stats["tier_counts"])
    except requests.exceptions.ConnectionError:
        st.error("Can't reach the API server at {API_URL}. Is it running? ")
                 #"(uvicorn api.main:app --reload --port 8000)")

# --- Main area: run the agent team on a topic ---
st.subheader("Write an article with the Researcher → Writer → Reviewer team")

topic = st.text_input("Topic", placeholder="e.g. Why the ocean is salty")
run_button = st.button("Run Agent Team", type="primary")

if run_button and topic.strip():
    with st.spinner("Researching, writing, and reviewing... this can take a minute."):
        try:
            resp = requests.post(
                f"{API_URL}/agent-team", json={"topic": topic}, timeout=180
            )
            resp.raise_for_status()
            #data = resp.json()
            st.session_state.last_result = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Can't reach the API server at {API_URL}. Is it running? ")
                     #"(uvicorn api.main:app --reload --port 8000)")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    #st.success("Done!")
    st.rerun()    
elif run_button:
    st.warning("Please enter a topic first.")

if st.session_state.last_result:
    data = st.session_state.last_result
    st.success("Done!")
    col1, col2 = st.columns([2, 1])


    with col1:
        st.subheader("📄 Final Article")
        st.write(data["final_output"])

        with st.expander("🔍 Research notes"):
            st.write(data["research_notes"])

        if data["revision_count"] > 0 and data.get("feedback"):
            with st.expander("📝 Last reviewer feedback"):
                st.write(data["feedback"])

    with col2:
        st.subheader("🧾 Routing Diary")
        total_cost = 0.0
        for i, entry in enumerate(data["routing_log"], 1):
            tag = "🟢" if entry["tier_used"] == "weak" else "🔵"
            fallback = " ⚠️ fallback" if entry.get("fallback_triggered") else ""
            st.markdown(
                f"**{i}. {tag} {entry['agent'].title()}** — "
                f"`{entry['tier_used']}` ({entry['model_used']}){fallback}\n\n"
                f"Score: {entry['complexity_score']} · "
                f"Cost: ${entry['estimated_cost_usd']:.6f}"
            )
            total_cost += entry["estimated_cost_usd"]

        st.metric("Total cost for this run", f"${total_cost:.6f}")
        st.metric("Revisions needed", data["revision_count"])

elif run_button:
    st.warning("Please enter a topic first.")

