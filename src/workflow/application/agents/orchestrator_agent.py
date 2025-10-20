from src.workflow.application.services.prompt_service import PromptService
from src.workflow.state import State
from src.workflow.domain.models import OrchestratorOutput
from src.workflow.domain.services.llm_service import LlmService
from src.shared.utils.decorators.error_hanlder import error_handler

class Orchestrator:
    __MODULE = "context_orchestrator.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    @error_handler(module=__MODULE)
    def __get_prompt(self, state: State):
        system_message = """
        You are a coding context orchestrator agent. Analyze the user's query to determine if it is related to coding or software engineering.

        Set coding = True if the query requires:
        - Programming concepts, languages, or frameworks
        - Software engineering principles or practices
        - Debugging, testing, or optimizing code
        - Development tools or environments

        Set fallback = True if the query:
        - Is unrelated to coding or software engineering
        - Is too vague or ambiguous to determine its relevance to coding

        Examples:
        - "How do I write a Python function?" - coding: True, fallback: False
        - "What is the best way to debug JavaScript?" - coding: True, fallback: False
        - "What is the weather today?" - coding: False, fallback: True
        - "Help" - coding: False, fallback: True
        """
        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=state["chat_history"],
            input=state["input"]
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State) -> OrchestratorOutput:   
        prompt = self.__get_prompt(state)

        response = await self.__llm_service.invoke_structured(
            prompt=prompt,
            response_model=OrchestratorOutput,
            temperature=0.0
        )

        return response