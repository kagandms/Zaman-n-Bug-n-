import tweepy
import requests
import os
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- 1. OPENROUTER (DEEPSEEK) İLE METİN YAZARLIĞI ---
def rewrite_with_deepseek(original_text):
    api_key = os.getenv("OPENROUTER_API_KEY") # GitHub'daki anahtarı alır
    if not api_key:
        print("UYARI: API Key bulunamadı, orijinal metin kullanılacak.")
        return original_text

    # ADRES DEĞİŞTİ: Artık OpenRouter'a gidiyoruz
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    system_prompt = (
        "Sen profesyonel bir sosyal medya yöneticisisin. Görevin, sana verilen tarihi olayı "
        "Twitter (X) platformu için viral olacak, merak uyandırıcı ve etkileşim alacak bir formata dönüştürmektir. "
        "\n\nKURALLAR:"
        "\n1. Cevabın SADECE ve SADECE atılacak tweet metninden oluşmalıdır."
        "\n2. ASLA 'İşte tweetiniz:', 'Revize edilmiş hali:', 'Öneri:' gibi giriş veya bitiş cümleleri yazma."
        "\n3. Tırnak işareti (\") içine alma."
        "\n4. Ansiklopedik dili bırak, samimi ve heyecanlı konuş."
        "\n5. 1-2 adet emoji kullan."
        "\n6. Tweetin sonuna takipçileri yorum yapmaya teşvik edecek kısa bir soru ekle."
        "\n7. Toplam uzunluk hashtagler dahil 240 karakteri geçmesin."
    )

    payload = {
        # MODEL İSMİ DEĞİŞTİ: OpenRouter formatına uygun hale geldi
        "model": "deepseek/deepseek-chat", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Metin: {original_text}"}
        ],
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kagandms/tarihte-bugun-botu", # OpenRouter için gerekli başlıklar
        "X-Title": "Tarihte Bugun Botu"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"OpenRouter API Hatası: {response.text}")
            return original_text
            
        result = response.json()
        
        # OpenRouter bazen farklı yanıt yapısı döndürebilir, kontrol edelim
        if 'choices' in result and len(result['choices']) > 0:
            new_text = result['choices'][0]['message']['content'].strip()
            
            # Temizlik
            new_text = new_text.replace('"', '').replace("'", "")
            if ":" in new_text[:20]: 
                new_text = new_text.split(":", 1)[1].strip()
                
            print("Yapay Zeka metni başarıyla revize etti! 🤖")
            return new_text
        else:
            print("API yanıtı beklendiği gibi değil.")
            return original_text
            
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return original_text

# --- 2. TWITTER BAĞLANTILARI ---
def get_twitter_api_v1():
    auth = tweepy.OAuthHandler(
        os.getenv("API_KEY"),
        os.getenv("API_SECRET")
    )
    auth.set_access_token(
        os.getenv("ACCESS_TOKEN"),
        os.getenv("ACCESS_TOKEN_SECRET")
    )
    return tweepy.API(auth)

def get_twitter_client_v2():
    return tweepy.Client(
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
    )

# --- 3. AKILLI VERİ ÇEKME ---
def get_smart_event():
    # TR Saati Ayarı
    today = datetime.now() + timedelta(hours=3)
    month = today.month
    day = today.day
    
    print(f"Tarih (TR): {day}.{month}")
    
    url = f"https://tr.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    headers = {
        'User-Agent': 'TarihBot/3.0 (https://twitter.com/TarihteNeOldu; me@example.com)'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, None
            
        data = response.json()
        events = data.get("events", [])
        
        if not events:
            return None, None

        # Önem Filtresi
        important_events = [e for e in events if len(e.get("pages", [])) >= 4]
        
        if important_events:
            print(f"Önemli olay bulundu ({len(important_events)} adet).")
            selected_event = random.choice(important_events)
        else:
            print("Önemli olay bulunamadı, rastgele seçiliyor.")
            selected_event = random.choice(events)

        year = selected_event.get("year")
        raw_text = selected_event.get("text")
        
        # --- YAPAY ZEKA DOKUNUŞU ---
        print(f"Orijinal: {raw_text}")
        ai_text = rewrite_with_deepseek(raw_text)
        
        # Tweet Metni
        tweet_text = f"📅 Tarihte Bugün ({day}.{month}.{year})\n\n{ai_text}\n\n#tarih #tarihteneoldu"
        
        # Görsel Kontrolü
        image_url = None
        if selected_event.get("pages"):
            first_page = selected_event["pages"][0]
            if "originalimage" in first_page:
                image_url = first_page["originalimage"]["source"]
            elif "thumbnail" in first_page:
                image_url = first_page["thumbnail"]["source"]

        return tweet_text, image_url

    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None, None

def download_image(url):
    filename = "temp_image.jpg"
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except Exception as e:
        print(f"Resim indirme hatası: {e}")
    return None

def main():
    api_v1 = get_twitter_api_v1()
    client_v2 = get_twitter_client_v2()
    
    print("Bot başlatılıyor...")
    tweet_text, image_url = get_smart_event()
    
    if tweet_text:
        media_id = None
        
        if image_url:
            print(f"Görsel indiriliyor: {image_url}")
            filename = download_image(image_url)
            if filename:
                try:
                    media = api_v1.media_upload(filename)
                    media_id = media.media_id
                    os.remove(filename)
                except Exception as e:
                    print(f"Görsel yüklenemedi: {e}")
        
        try:
            if media_id:
                client_v2.create_tweet(text=tweet_text, media_ids=[media_id])
                print("Görselli tweet başarıyla atıldı! 📸")
            else:
                client_v2.create_tweet(text=tweet_text)
                print("Metin tweet başarıyla atıldı! 📝")
        except Exception as e:
            print(f"Tweet gönderme hatası: {e}")
    else:
        print("İçerik bulunamadı.")

if __name__ == "__main__":
    main()