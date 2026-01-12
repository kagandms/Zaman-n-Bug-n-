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
        return original_text, []

    # ADRES DEĞİŞTİ: Artık OpenRouter'a gidiyoruz
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    system_prompt = (
        "Sen profesyonel bir sosyal medya yöneticisisin. Görevin, sana verilen tarihi olayı "
        "Twitter (X) platformu için viral olacak, merak uyandırıcı ve etkileşim alacak bir formata dönüştürmektir. "
        "\n\nKURALLAR:"
        "\n1. Cevabın SADECE atılacak tweet metninden oluşmalıdır."
        "\n2. ASLA 'İşte tweetiniz:', 'Revize edilmiş hali:' gibi giriş veya bitiş cümleleri yazma."
        "\n3. Ansiklopedik dili bırak, samimi ve heyecanlı konuş."
        "\n4. 1-2 adet emoji kullan."
        "\n5. Tweetin en sonuna (yeni satıra geçmeden) takipçilerle etkileşim kuracak 2 veya 3 şıklı bir anket sorusu ekle."
        "\nFORMAT:"
        "\n[Tweet Metni]"
        "\nANKET: [Seçenek 1] | [Seçenek 2] | [Seçenek 3]"
        "\nÖrnek Çıktı:"
        "\nFatih Sultan Mehmet İstanbul'u fethetti! 🏰 Peki sizce tarihin en büyük komutanı kim? ⚔️"
        "\nANKET: Fatih Sultan Mehmet | Büyük İskender | Napolyon"
        "\n6. Toplam uzunluk hashtagler dahil 240 karakteri geçmesin."
    )

    payload = {
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
        "HTTP-Referer": "https://github.com/kagandms/tarihte-bugun-botu",
        "X-Title": "Tarihte Bugun Botu"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"OpenRouter API Hatası: {response.text}")
            return original_text, []
            
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content'].strip()
            
            # İçerik Temizliği
            content = content.replace('"', '').replace("'", "")
            
            # Anket Ayrıştırma
            tweet_text = content
            poll_options = []
            
            if "ANKET:" in content:
                parts = content.split("ANKET:")
                tweet_text = parts[0].strip()
                raw_poll = parts[1].strip()
                poll_options = [opt.strip() for opt in raw_poll.split("|") if opt.strip()]
                # Limit to 3 options
                poll_options = poll_options[:3]

            print("Yapay Zeka metni ve anketi başarıyla revize etti! 🤖")
            return tweet_text, poll_options
        else:
            print("API yanıtı beklendiği gibi değil.")
            return original_text, []
            
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return original_text, []

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
# --- 3. AKILLI VERİ ÇEKME ---
def get_smart_event():
    # TR Saati Ayarı
    today = datetime.now() + timedelta(hours=3)
    month = today.month
    day = today.day
    
    print(f"Tarih (TR): {day}.{month}")
    
    # Tüm kategorilerden veri çekip havuz oluşturacağız
    categories = ["events", "births", "deaths"]
    all_important_items = []
    all_items = []
    
    headers = {
        'User-Agent': 'TarihBot/3.0 (https://twitter.com/TarihteNeOldu; me@example.com)'
    }

    try:
        # Her kategori için API çağrısı
        for cat in categories:
            url = f"https://tr.wikipedia.org/api/rest_v1/feed/onthisday/{cat}/{month}/{day}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get(cat, [])
                if items:
                    for item in items:
                        # Kategori bilgisini öğeye ekle (daha sonra emoji için lazım)
                        item["_category"] = cat
                        all_items.append(item)
                        
                        # Önem Filtresi: Events için 4+, diğerleri için 2+ kaynak
                        min_pages = 4 if cat == "events" else 2
                        if len(item.get("pages", [])) >= min_pages:
                            all_important_items.append(item)

        if not all_items:
            return None, None, []

        # Seçim Yapma
        if all_important_items:
            print(f"Toplam {len(all_important_items)} önemli içerik bulundu.")
            selected_item = random.choice(all_important_items)
        else:
            print("Önemli içerik bulunamadı, genel havuzdan seçiliyor.")
            selected_item = random.choice(all_items)

        # Veri Ayrıştırma
        category = selected_item.get("_category", "events")
        year = selected_item.get("year")
        raw_text = selected_item.get("text")
        
        # --- YAPAY ZEKA DOKUNUŞU ---
        print(f"Seçilen Kategori: {category} | Orijinal: {raw_text}")
        ai_text, poll_options = rewrite_with_deepseek(raw_text)
        
        # Emoji Seçimi
        emoji_map = {"events": "📅", "births": "🎂", "deaths": "🕊️"}
        header_emoji = emoji_map.get(category, "📅")
        
        # Tweet Metni
        tweet_text = f"{header_emoji} Tarihte Bugün ({day}.{month}.{year})\n\n{ai_text} #tarih #tarihteneoldu"
        
        # Görsel Kontrolü
        image_url = None
        if selected_item.get("pages"):
            first_page = selected_item["pages"][0]
            if "originalimage" in first_page:
                image_url = first_page["originalimage"]["source"]
            elif "thumbnail" in first_page:
                image_url = first_page["thumbnail"]["source"]

        return tweet_text, image_url, poll_options

    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None, None, []

    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None, None
        tweet_text = f"📅 Tarihte Bugün ({day}.{month}.{year})\n\n{ai_text} #tarih #tarihteneoldu"
        
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
    tweet_text, image_url, poll_options = get_smart_event()
    
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
            # Tweet Parametreleri
            tweet_params = {"text": tweet_text}
            
            if media_id:
                tweet_params["media_ids"] = [media_id]
                
            if poll_options and len(poll_options) >= 2:
                # Anket varsa ekle (Süre: 24 saat = 1440 dakika)
                tweet_params["poll_options"] = poll_options
                tweet_params["poll_duration_minutes"] = 1440
                print(f"Anket eklendi: {poll_options}")

            client_v2.create_tweet(**tweet_params)
            print("Tweet başarıyla atıldı! 🚀")
            
        except Exception as e:
            print(f"Tweet gönderme hatası: {e}")
    else:
        print("İçerik bulunamadı.")

if __name__ == "__main__":
    main()