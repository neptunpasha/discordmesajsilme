# Discord Message Purge Tool (By Neptun Pasha)

Discord üzerinde kendi yazdığınız mesajları hızlı ve dinamik bir şekilde temizlemenizi sağlayan, eğitim ve kişisel kullanım amaçlı geliştirilmiş gelişmiş bir konsol (CLI) aracıdır.

## 🌟 Özellikler

- **Token Kaydetme Sistemi:** Her açılışta token girmekle uğraşmayın, tokeniniz yerel olarak güvenli bir şekilde `token.txt` dosyasında saklanır. (.gitignore ile korunmaktadır)
- **Dinamik Arkadaş Listesi Entegrasyonu:** Sadece aktif DM kanallarınızı değil, arkadaş listenizdeki herkesi otomatik çekip onlarla yeni DM kanalları açarak geçmişi temizleyebilir.
- **Sunucu ve Kanal Yönetimi:** Sunuculardaki tüm yazılı kanalları otomatik listeler. İster tek bir kanalı, ister sunucudaki tüm kanalları (`all` komutuyla) tek seferde temizleyebilirsiniz.
- **Gelişmiş Hız Modları:**
  - *Güvenli (Slow):* 2.5 - 4.5 saniye rastgele bekleme (Önerilen).
  - *Hızlı (Medium):* 0.5 - 1.2 saniye bekleme.
  - *Turbo (Fast):* 0.05 - 0.20 saniye bekleme (Dinamik Hız Sınırı Algılamalı).
- **Dinamik Rate Limit Algılayıcı (HTTP 429):** Discord'un hız sınırlarına takıldığında otomatik duraklayıp, Discord'un tam olarak talep ettiği süre kadar bekledikten sonra son hızda devam eder.
- **Kelime Filtresi (Word Filter):** İsteğe bağlı olarak sadece belirli bir kelimeyi/cümleyi içeren mesajlarınızı temizleyebilirsiniz.

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Bilgisayarınızda [Python 3.8+](https://www.python.org/) yüklü olmalıdır.

### Adımlar

1. Bu depoyu klonlayın veya zip olarak indirin:
   ```bash
   git clone https://github.com/neptunpasha/discordmesajsilme.git
   cd discordmesajsilme
