from src.workflow.application.services.prompt_service import PromptService
from src.workflow.state import State
from src.workflow.domain.services.llm_service import LlmService
from src.shared.application.use_cases.ws_streaming import WsStreaming
from src.shared.utils.decorators.error_hanlder import error_handler

class CodeAssistant:
    __MODULE = "coding_assistant.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService, streaming: WsStreaming):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__streaming = streaming

    @error_handler(module=__MODULE)
    def __get_prompt(self, state: State):
        system_message = """
        You are an expert full-stack software engineer and coding assistant. Your role is to help the user write, update, and structure code that is maintainable, scalable, and secure.

        Guidelines:
        - Always follow best practices for software architecture, security, and coding standards.
        - Provide clear, concise, and well-documented solutions.
        - Ensure the code is optimized for performance and readability.
        - When applicable, explain your reasoning or suggest alternative approaches.
        - Avoid introducing unnecessary complexity.

        Your goal is to empower the user to write high-quality code while adhering to industry standards.
        """
        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=state["chat_history"],
            input=state["input"]
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State) -> str:   
        prompt = self.__get_prompt(
            state=state
        )

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