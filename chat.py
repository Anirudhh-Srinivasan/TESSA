import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

hotel_info = open("hotel_info.md").read()

system_prompt = f"""You are the front desk assistant for the hotel below.
Answer only using this information. If the answer isn't here, say you don't know
and offer to connect them with a human.

{hotel_info}"""

messages = [{"role": "system", "content": system_prompt}]

while True:
    user_input = input("You: ")
    if user_input.lower() in ("quit", "exit"):
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )

    reply = response.choices[0].message.content
    print("Bot:", reply)

    messages.append({"role": "assistant", "content": reply})


    