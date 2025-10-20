from src.workflow.application.services.prompt_service import PromptService
from src.workflow.domain.services.llm_service import LlmService
from src.shared.application.use_cases.ws_streaming import WsStreaming
from src.workflow.state import State
from src.shared.utils.decorators.error_hanlder import error_handler

class FallBackAgent:
    __MODULE = "fallback.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        streaming: WsStreaming
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__streaming = streaming

    @error_handler(module=__MODULE)
    def __get_prompt(
        self,
        state: State
    ):
        system_message = """
        You are a legal assistant fallback agent.

        The user's request has already been determined to be outside the scope of this assistant, or is too vague to answer.

        Politely inform the user that you cannot assist with their request because it is either outside the scope of this assistant or lacks sufficient detail.

        Clearly explain that your expertise is limited to legal topics, including:
        - General legal principles, statutes, and regulations
        - Company-specific legal documents and policies
        - Legal compliance and related matters
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        If the user would like help with a legal question, encourage them to ask about those topics and provide more specific details if possible.
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=state["input"]
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(
        self,
        state: State
    ): 
        prompt = self.__get_prompt(state=state)

        chunks = []
        async for chunk in self.__llm_service.generate_stream(
            prompt=prompt,
            temperature=0.5
        ):
            chunks.append(chunk)

            await self.__streaming.execute(
                ws_connection_id=state["chat_id"],
                text=chunk,
                voice=False
            )
        
        return "".join(chunks)