from main import get_smart_event, generate_ai_reply
import os
from dotenv import load_dotenv

load_dotenv()

print("--- Final v2 Debug with History ---")

# 1. Thread & Poll Test
print("\n--- Testing Thread Generation (and History Check) ---")
# returns final_tweets, image_url, poll_options, raw_text
t_thread, i, polls, r_text = get_smart_event()

if t_thread:
    print(f"Thread Length: {len(t_thread)}")
    print(f"Raw Text (for history): {r_text[:40]}...")
else:
    print("No content selected (possibly empty pool).")

# 2. Interaction AI Test
print("\n--- Testing Reply AI ---")
reply = generate_ai_reply("Harika bir bilgi, teşekkürler! Ankara Savaşı hakkında ne düşünüyorsun?")
print(f"AI Reply: {reply}")
