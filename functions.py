"""Python implementations of the callable tools and their schemas."""

from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass
from memory import Memory


@dataclass
class Parameter:
    """Represents a function parameter with its type and requirements."""
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


class ToolFunction:
    """Base class for defining tool functions in a human-friendly way."""
    
    name: str
    description: str
    parameters: List[Parameter]
    
    @classmethod
    def execute(cls, memory: Memory, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the function with the given arguments."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    @classmethod
    def to_schema(cls) -> Dict[str, Any]:
        """Convert the function definition to OpenAI tool schema format."""
        properties = {}
        required = []
        
        for param in cls.parameters:
            param_schema = {"type": param.type}
            if param.enum:
                param_schema["enum"] = param.enum
            properties[param.name] = param_schema
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


# Example function definitions
class NewMemoryInsert(ToolFunction):
    name = "new_memory_insert"
    description = "Infer a new memory and append it to a memory store."
    parameters = [
        Parameter(
            name="memory_type",
            type="string",
            description="Type of memory to insert",
            enum=["core", "semantic", "episodic"]
        ),
        Parameter(
            name="content",
            type="string",
            description="Content of the memory to insert"
        ),
    ]
    
    @classmethod
    def execute(cls, memory: Memory, arguments: Dict[str, Any]) -> Dict[str, Any]:
        memory.new_memory_insert(arguments["memory_type"], arguments["content"])
        return {"status": "ok"}


class MemoryUpdate(ToolFunction):
    name = "memory_update"
    description = "Update an existing memory by index."
    parameters = [
        Parameter(
            name="memory_type",
            type="string",
            description="Type of memory to update",
            enum=["core", "semantic", "episodic"]
        ),
        Parameter(
            name="index",
            type="integer",
            description="Index of the memory to update"
        ),
        Parameter(
            name="new_content",
            type="string",
            description="New content for the memory"
        ),
    ]
    
    @classmethod
    def execute(cls, memory: Memory, arguments: Dict[str, Any]) -> Dict[str, Any]:
        memory.memory_update(
            arguments["memory_type"],
            arguments["index"],
            arguments["new_content"]
        )
        return {"status": "ok"}


class MemoryConsolidate(ToolFunction):
    name = "memory_consolidate"
    description = "Deduplicate memories of a given type."
    parameters = [
        Parameter(
            name="memory_type",
            type="string",
            description="Type of memory to consolidate",
            enum=["core", "semantic", "episodic"]
        ),
    ]
    
    @classmethod
    def execute(cls, memory: Memory, arguments: Dict[str, Any]) -> Dict[str, Any]:
        memory.memory_consolidate(arguments["memory_type"])
        return {"status": "ok"}


class MemoryDelete(ToolFunction):
    name = "memory_delete"
    description = "Delete a memory by index."
    parameters = [
        Parameter(
            name="memory_type",
            type="string",
            description="Type of memory to delete",
            enum=["core", "semantic", "episodic"]
        ),
        Parameter(
            name="index",
            type="integer",
            description="Index of the memory to delete"
        ),
    ]
    
    @classmethod
    def execute(cls, memory: Memory, arguments: Dict[str, Any]) -> Dict[str, Any]:
        memory.memory_delete(arguments["memory_type"], arguments["index"])
        return {"status": "ok"}


# List of all available tool functions
TOOL_FUNCTIONS = [
    NewMemoryInsert,
    MemoryUpdate,
    MemoryConsolidate,
    MemoryDelete,
]

# Generate the function implementations map
FUNCTION_IMPLS = {
    func.name: func.execute for func in TOOL_FUNCTIONS
}

# Generate the OpenAI tool schemas
TOOL_SCHEMAS = [
    func.to_schema() for func in TOOL_FUNCTIONS
]