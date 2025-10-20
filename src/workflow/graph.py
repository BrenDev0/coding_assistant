from fastapi import Depends
from typing import List
import os
from langgraph.graph import StateGraph, END, START
import httpx

from src.workflow.state import State
from src.workflow.application.agents.orchestrator_agent import Orchestrator
from src.workflow.dependencies import get_orchestrator
from src.workflow.domain.models import OrchestratorOutput
from src.workflow.application.agents.code_assistant import CodeAssistant
from src.workflow.dependencies import get_coding_agent


from src.workflow.application.agents.fallback_agent import FallBackAgent
from src.workflow.dependencies import get_fallback_agent

from src.shared.utils.http.get_hmac_header import generate_hmac_headers


def create_graph(
    context_orchestrator_agent: Orchestrator = Depends(get_orchestrator),
    general_legal_researcher: CodeAssistant = Depends(get_coding_agent),
    fallback_agent: FallBackAgent = Depends(get_fallback_agent)
):
    graph = StateGraph(State)


    async def orchestrator_node(state: State):       
        response =  await context_orchestrator_agent.interact(state=state)

        return {"orchestrator_response": response}
    

    def orchestrate(state: State) -> List[str]:
        orchestrator_response: OrchestratorOutput = state["orchestrator_response"]
        next_nodes = []

        if orchestrator_response.general_law:
            next_nodes.append("general_legal_research")

        if orchestrator_response.company_law:
            next_nodes.append("company_legal_research")
        
        if not next_nodes:
            next_nodes.append("fallback")
        
        return next_nodes
    

    async def coding_node(state: State):
        response = await general_legal_researcher.interact(state=state)

        return {"general_legal_response": response}

    
    async def fallback_node(state: State):
        response = await fallback_agent.interact(state=state)
        return {"final_response": response}
    
    async def hanlde_response_node(state: State):
        hmac_headers = generate_hmac_headers(os.getenv("HMAC_SECRET"))
        main_server = os.getenv("MAIN_SERVER_ENDPOINT")
        req_body = {
            "sender": os.getenv("AGENT_ID"),
            "message_type": "ai",
            "text": state["final_response"]
        }
        
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{main_server}/messages/internal/{state['chat_id']}",
                headers=hmac_headers,
                json=req_body
            )

            if res.status_code != 201:
                print("POST response:", res)

            return state
            

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("coding", coding_node)
    graph.add_node("fallback", fallback_node)
    graph.add_node("handle_response", hanlde_response_node)
    
    graph.add_edge(START, "orchestrator")
    
    graph.add_conditional_edges(
        "orchestrator",
        orchestrate,
        {
            "coding": "coding",
            "fallback": "fallback"
        }
    )

    graph.add_edge("coding", "handle_response")
    graph.add_edge("fallback", "handle_response")
    graph.add_edge("handle_response", END)


    return graph.compile()
   

