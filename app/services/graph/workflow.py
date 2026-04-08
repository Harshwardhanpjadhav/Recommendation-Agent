from langgraph.graph import StateGraph, END


from app.services.graph.state import AgentState
from app.services.graph.nodes import *



# Add our custom agent node
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)

workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app_brain = workflow.compile()