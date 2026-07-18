import asyncio
import os
from src.core.config import settings
from src.data.database import init_db, engine
from sqlalchemy import text

async def verify_connection():
    print(f"🔌 Bağlantı Testi: {settings.DATABASE_URL}")
    
    # 1. Dosya var mı?
    db_file = "bot_data.db"
    if os.path.exists(db_file):
        print(f"📂 Veritabanı dosyası mevcut: {db_file}")
    else:
        print(f"📂 Veritabanı dosyası henüz YOK. Oluşturulacak...")

    # 2. Bağlan ve Tabloları Yarat
    try:
        await init_db()
        print("✅ Tablolar başarıyla oluşturuldu/doğrulandı.")
    except Exception as e:
        print(f"❌ Başlatma Hatası: {e}")
        return

    # 3. Basit Sorgu At
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.scalars().all()
        print(f"📊 Mevcut Tablolar: {tables}")
        
    print("🚀 Sistem çalışıyor ve veritabanına bağlı!")

if __name__ == "__main__":
    asyncio.run(verify_connection())
