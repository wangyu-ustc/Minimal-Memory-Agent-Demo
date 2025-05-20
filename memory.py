from __future__ import annotations
from typing import List


class Memory:
    """Holds core, semantic, episodic memories entirely in RAM."""

    # Maximum number of items to show for semantic and episodic memories
    MAX_MEMORY_ITEMS = 5

    def __init__(self) -> None:
        self.core: List[str] = []
        self.semantic: List[str] = []
        self.episodic: List[str] = []

    # --------------------------------------------------
    # Rendering helpers
    # --------------------------------------------------
    def _block(self, title: str, lines: List[str]) -> str:
        body = "\n".join(lines) if lines else "Empty."
        return f"<{title}>\n{body}\n</{title}>"

    def render_system_prompt(self) -> str:
        """Return the system prompt expected by the model."""
        # For semantic and episodic memories, only show the most recent items
        semantic_items = self.semantic[-self.MAX_MEMORY_ITEMS:] if self.semantic else []
        episodic_items = self.episodic[-self.MAX_MEMORY_ITEMS:] if self.episodic else []
        
        return (
            "You are a personal assistant that needs to memorize the information in the memory "
            "and retrieve the relevant information when queried.\n\n"
            f"{self._block('core_memory', self.core)}\n\n"
            f"{self._block('semantic_memory', semantic_items)}\n\n"
            f"{self._block('episodic_memory', episodic_items)}"
        )

    # --------------------------------------------------
    # Memory operations – called by functions.py
    # --------------------------------------------------
    def new_memory_insert(self, memory_type: str, content: str):
        getattr(self, memory_type).append(content)

    def memory_update(self, memory_type: str, index: int, new_content: str):
        mem_list = getattr(self, memory_type)
        if 0 <= index < len(mem_list):
            mem_list[index] = new_content

    def memory_consolidate(self, memory_type: str):
        # Toys: just deduplicate identical lines
        mem_list = getattr(self, memory_type)
        unique: List[str] = []
        [unique.append(x) for x in mem_list if x not in unique]
        setattr(self, memory_type, unique)

    def memory_delete(self, memory_type: str, index: int):
        mem_list = getattr(self, memory_type)
        if 0 <= index < len(mem_list):
            mem_list.pop(index)


# ===========================
# File: functions.py
# ---------------------------
"""Python implementations of the callable tools."""

from typing import Any, Dict
from memory import Memory


def new_memory_insert(memory: Memory, arguments: Dict[str, Any]):
    memory.new_memory_insert(arguments["memory_type"], arguments["content"])
    return {"status": "ok"}


def memory_update(memory: Memory, arguments: Dict[str, Any]):
    memory.memory_update(arguments["memory_type"], arguments["index"], arguments["new_content"])
    return {"status": "ok"}


def memory_consolidate(memory: Memory, arguments: Dict[str, Any]):
    memory.memory_consolidate(arguments["memory_type"])
    return {"status": "ok"}


def memory_delete(memory: Memory, arguments: Dict[str, Any]):
    memory.memory_delete(arguments["memory_type"], arguments["index"])
    return {"status": "ok"}


# Map function names → callables, used by agent.py
FUNCTION_IMPLS = {
    "new_memory_insert": new_memory_insert,
    "memory_update": memory_update,
    "memory_consolidate": memory_consolidate,
    "memory_delete": memory_delete,
}