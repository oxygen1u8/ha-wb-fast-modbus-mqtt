from pydantic import BaseModel, Field, field_validator
from typing import Literal


class JSONContent(BaseModel):
    content: str = Field(..., description="Содержимое конфигурации в формате JSON")

    @field_validator("content")
    @classmethod
    def validate_json_content(cls, json_content: str):
        try:
            json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Content of field 'content' has invalid JSON format: {str(e)}"
            )
        return json_content
