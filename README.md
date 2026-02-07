# 📊 Advanced Discord Stats & Economy Bot

Bu proje, Discord sunucuları için geliştirilmiş, **veritabanı destekli (SQLite)**, detaylı istatistik, seviye, ekonomi ve yönetim botudur.

Bot, kullanıcıların mesaj, ses, yayın ve oyun aktivitelerini saniye saniye takip eder, bunları veritabanına kaydeder ve "Canlı (Live)" verilerle birleştirerek anlık liderlik tabloları sunar.

## 🔥 Özellikler

### 📈 İstatistik Sistemi
* **Detaylı Takip:** Mesaj sayısı, sesli sohbet süresi, yayın (stream) süresi ve oyun oynama süresi.
* **Periyodik Veriler:** Günlük, Haftalık, Aylık ve Tüm Zamanlar (Total) istatistikleri.
* **Canlı Veri (Live Tracking):** `/top` veya `/stats` komutu kullanıldığında, o an seste olan veya oyun oynayan kişilerin süreleri anlık olarak veritabanı verisiyle birleştirilir.
* **Oyun Takibi:** Kullanıcıların hangi oyunu ne kadar süre oynadığını kaydeder ve profilde listeler.

### 🏆 Sıralama & Liderlik (Leaderboard)
* **Kullanıcı Sıralaması:** En çok mesaj atan, en çok seste duran, en çok yayın açanlar.
* **Kanal Sıralaması:** Sunucunun en aktif metin ve ses kanalları.

### ⚔️ Rekabet & Sosyal
* **Rank Kartı (Resimli):** `/rank` komutu ile kullanıcının seviyesini, XP'sini ve sıralamasını gösteren özel tasarım resim oluşturulur (Pillow kütüphanesi ile).
* **Versus (VS):** `/vs @kullanıcı` komutu ile iki kişinin istatistikleri karşılaştırılır.
* **Reputation (Rep):** Kullanıcılar birbirine `/rep` ile saygınlık puanı verebilir (24 saatte bir).

### 📜 Görev Sistemi (Quests)
* **Günlük Görevler:** Her kullanıcıya özel günlük rastgele hedefler (Örn: 50 mesaj at, 30dk oyun oyna).
* **Otomatik Takip:** Aktiviteler yapıldıkça görev ilerlemesi otomatik güncellenir.

### 🌍 Çoklu Dil Desteği (Multi-Language)
* **TR / EN:** Sunucu yöneticisi `/setup` veya `/lang` üzerinden botun dilini Türkçe veya İngilizce yapabilir.
* **Kalıcı Ayar:** Dil tercihi veritabanına kaydedilir.

### ⚙️ Gelişmiş Yönetim Paneli (Admin)
* **Modüler Yapı:** Rol sistemi, Level sistemi, Görev sistemi ve Gazete sistemi `/setup` menüsünden tek tıkla açılıp kapatılabilir.
* **Veri Güvenliği (Wipe & Restore):** * Bir kullanıcının veya **Tüm Sunucunun** verileri silinebilir.
    * **Arşivleme:** Silinen veriler JSON formatında arşivlenir.
    * **Geri Yükleme (Merge):** Silinen veriler geri yüklendiğinde, mevcut verilerin üzerine eklenir (Veri kaybı yaşanmaz).

---

# 🚀 Kurulum Rehberi (Adım Adım)

Bu botu bilgisayarında veya sunucunda çalıştırmak için aşağıdaki adımları sırasıyla yapman yeterli.

### 1. Gerekli Programları İndir
Öncelikle bilgisayarında **Python** yüklü olmalı.
1. [Python İndir](https://www.python.org/downloads/) adresine git.
2. İndirirken **"Add Python to PATH"** kutucuğunu MUTLAKA işaretle (Yoksa komutlar çalışmaz).
3. Kurulumu tamamla.

### 2. Dosyaları Hazırla
1. Bu projeyi bilgisayarına indir (Zip olarak indirip masaüstüne bir klasöre çıkart).
2. Klasörün içinde şu dosyaların olduğundan emin ol:
   * `main.py` (Botu başlatan dosya)
   * `database.py` (Veritabanı sistemi)
   * `cogs/` klasörü ve içinde `stats.py`
   * `requirements.txt`

### 3. Kütüphaneleri Yükle (Terminal İşlemi)
1. Botun klasörüne gir.
2. Klasör yoluna (adres çubuğuna) `cmd` yaz ve Enter'a bas. (Siyah bir ekran açılacak).
3. Açılan ekrana şu komutu yapıştır ve Enter'a bas:
   ```bash
   pip install -r requirements.txt
4. Yükelem bittikten sonra
   ```bash
   python main.py
ile başlat

TOKENİ MAİN.PY İÇİNE YAZACAKSINIZ UNUTMAYIN
