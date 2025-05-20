"""Simple CLI loop."""

from agent import SleepTimeComputeAgent


def main():
    agent = SleepTimeComputeAgent()
    print("SleepTimeCompute agent is ready. Type 'exit' to quit.\n")
    while True:
        user = input("User: ")
        if user.lower() in {"exit", "quit"}:
            break
        agent.chat(user)


if __name__ == "__main__":
    main()