import json
import os
from typing import Any, Dict, List

import openai
from dotenv import load_dotenv

from memory import Memory
from functions import FUNCTION_IMPLS, TOOL_SCHEMAS


class SleepTimeComputeAgent:
    """Event‑loop agent that lets the model call memory‑editing tools."""

    MODEL = "gpt-4.1-mini"  # replace with actual model name when available
    MAX_CONVERSATION_TURNS = 5  # Maximum number of conversation turns to include in history

    def __init__(self, include_conversation_history: bool = True) -> None:
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        self.memory = Memory()
        self.include_conversation_history = include_conversation_history
        self.conversation_history: List[Dict[str, Any]] = []

    # ---------------------------------------------
    # Public API
    # ---------------------------------------------
    def chat(self, user_msg: str):
        """Single chat turn including possible tool sub‑turns."""
        system_prompt = self.memory.render_system_prompt()
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history if enabled, limited to MAX_CONVERSATION_TURNS
        if self.include_conversation_history:
            # Each turn consists of 2 messages (user + assistant), so multiply by 2
            recent_history = self.conversation_history[-(self.MAX_CONVERSATION_TURNS * 2):]
            messages.extend(recent_history)
            
        messages.append({"role": "user", "content": user_msg})

        while True:
            response = self._complete(messages)
            assistant_msg = response.choices[0].message
            messages.append(assistant_msg)

            # If LLM decided to call tool(s) we must answer each with role="tool"
            if assistant_msg.tool_calls:
                for call in assistant_msg.tool_calls:
                    tool_result = self._run_tool(call)  # returns dict
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": call.function.name,
                            "content": json.dumps(tool_result),
                        }
                    )
                # Loop again so model can produce a real "assistant" reply
                continue

            # No tool calls – we are done this turn.
            print(f"Assistant: {assistant_msg.content}\n")
            
            # Store the conversation turn in history if enabled
            if self.include_conversation_history:
                self.conversation_history.extend([
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": assistant_msg.content}
                ])
            break

    # ---------------------------------------------
    # OpenAI helpers
    # ---------------------------------------------
    def _complete(self, messages):
        return self.client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            stream=False,
        )

    # ---------------------------------------------
    # Tool plumbing
    # ---------------------------------------------
    def _run_tool(self, call):
        name = call.function.name
        try:
            arguments: Dict[str, Any] = json.loads(call.function.arguments)
            result = FUNCTION_IMPLS[name](self.memory, arguments)
            return f"[tool {name} executed] → {result}"
        except json.JSONDecodeError as e:
            return f"[tool {name} error] Invalid JSON arguments: {str(e)}"
        except KeyError as e:
            return f"[tool {name} error] Missing required argument: {str(e)}"
        except ValueError as e:
            return f"[tool {name} error] Invalid argument value: {str(e)}"
        except Exception as e:
            return f"[tool {name} error] Unexpected error: {str(e)}"