from main import get_smart_event, generate_ai_reply
import os
from dotenv import load_dotenv

load_dotenv()

print("--- Final v2 Debug ---")

# 1. Thread & Poll Test
print("\n--- Testing Thread Generation ---")
t_thread, i, polls = get_smart_event()
print(f"Thread Length: {len(t_thread)}")
for idx, tweet in enumerate(t_thread):
    print(f"Tweet {idx+1}: {tweet[:50]}...")

if polls:
    print(f"Polls: {polls}")
else:
    print("No polls generated.")

# 2. Interaction AI Test
print("\n--- Testing Reply AI ---")
reply = generate_ai_reply("Harika bir bilgi, teşekkürler! Ankara Savaşı hakkında ne düşünüyorsun?")
print(f"AI Reply: {reply}")
