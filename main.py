from assistant import Assistant

jarvis = Assistant()

print("Jarvis is online.\n")

while True:
    prompt = input("> ")

    if prompt == "/exit":
        break

    print("Jarvis:", jarvis.ask(prompt))