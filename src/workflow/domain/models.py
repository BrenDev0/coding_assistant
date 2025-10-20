from pydantic import BaseModel, Field

class OrchestratorOutput(BaseModel):
    coding: bool = Field(
        False, 
        description="True if the query requires information coding, coding practices, or software engineering"
    )
    fallback: bool = Field(
        False, 
        description="True if the query has nothing to do with coding or software engineering"
    )
 