from langgraph.graph import StateGraph, END
from app.services.graph.state import AgentState
from app.services.graph.nodes import context_node, planner_node, coder_node, git_node,pr_node

workflow = StateGraph(AgentState)

# Add all 4 Nodes
workflow.add_node("context", context_node)
workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)
workflow.add_node("git", git_node)
workflow.add_node("pr", pr_node) # <--- The Finisher

# Define the Linear Path
workflow.set_entry_point("context")
workflow.add_edge("context", "planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "git") # <--- Coder passes to Git
workflow.add_edge("git", "pr") # <--- Push flows to PR
workflow.add_edge("git", END)

app_brain = workflow.compile()