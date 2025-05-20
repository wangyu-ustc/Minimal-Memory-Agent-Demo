"""Simple CLI loop."""

from agent import MemoryAgent


def main():
    agent = MemoryAgent()
    print("SleepTimeCompute agent is ready. Type 'exit' to quit.\n")
    while True:
        user = input("User: ")
        if user.lower() in {"exit", "quit"}:
            break
        agent.chat(user)


if __name__ == "__main__":
    main()