# Otomatik Kripto Arbitraj Tarayıcısı

Bu repo, Binance ve CoinGecko arasındaki fiyat farklılıklarını izleyerek potansiyel arbitraj fırsatlarını belirlemeye yardımcı olan basit bir otomasyon içerir. Arbitraj, aynı varlığın farklı piyasalardaki fiyat farklarından faydalanarak kâr etme stratejisidir. Script'i belirli aralıklarla çalıştırarak yüksek marjlı fırsatları hızlıca görebilir ve manuel işlem stratejilerinize entegre edebilirsiniz.

## Nasıl Çalışır?

`automation.py` aşağıdaki adımları uygular:

1. **Binance fiyatlarını çekme:** `--symbols` parametresiyle belirttiğiniz işlem çiftlerinin anlık fiyatlarını Binance API'sinden alır.
2. **CoinGecko fiyatlarını çekme:** Aynı işlem çiftlerinin (USDT bazlı) fiyatlarını CoinGecko'nun herkese açık API'sinden çeker.
3. **Fiyat farkını hesaplama:** İki borsadaki fiyatları karşılaştırır ve yüzdesel farkı hesaplar.
4. **Filtreleme:** `--threshold` değeriyle belirlenen eşik üzerinde fark oluşursa, fırsatı konsola yazar ve opsiyonel olarak CSV dosyasına kaydeder.

Bu süreç Cron, sistemd timer veya bir workflow aracıyla otomatikleştirilebilir. Elde edilen verileri kendi işlem altyapınıza bağlayarak manuel ya da yarı otomatik al-sat kararları için kullanabilirsiniz.

## Adım Adım Kurulum ve Çalıştırma

1. **Python 3 kurulu olduğundan emin olun.** Terminalde `python --version` yazarak kontrol
   edebilirsiniz. Sürüm 3.8 veya üzeri yeterlidir.
2. **Repo dosyalarını bilgisayarınıza indirin.**
   ```bash
   git clone https://github.com/<kullanıcı-adınız>/abayli.git
   cd abayli
   ```
   ZIP olarak indirdiyseniz dosyaları açıp klasöre girmeniz yeterli.
3. **(Opsiyonel) Sanal ortam oluşturun.** Script yalnızca standart kütüphaneleri
   kullansa da projeyi izole etmek için önerilir.
   ```bash
   python -m venv .venv
   # macOS/Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```
4. **Script'i çalıştırın.**
   ```bash
   python automation.py --symbols BTCUSDT ETHUSDT --threshold 0.8 --csv opportunities.csv
   ```
   İnternet bağlantınız olması gerekir; Binance veya CoinGecko'ya erişimin engellendiği
   ağlarda script çalışmayacaktır.

### Parametreler

- `--symbols`: İzlenecek Binance işlem çiftleri. Varsayılan olarak BTCUSDT ve ETHUSDT.
- `--threshold`: Yüzdesel fark eşiği. Varsayılan %0.5.
- `--csv`: Belirtirseniz fırsatlar CSV dosyasına eklenir.
- `--help`: Tüm seçeneklerin özetini gösterir.

Script'i tekrar tekrar çalıştırmak isterseniz Linux/macOS için `watch` ya da `cron`,
Windows için Görev Zamanlayıcı kullanabilirsiniz. Örneğin her 15 dakikada bir çalıştırmak
için Linux'ta `crontab -e` dosyanıza aşağıdaki satırı ekleyebilirsiniz:

```
*/15 * * * * /usr/bin/python /path/to/abayli/automation.py --symbols BTCUSDT ETHUSDT
```

Örnek çıktı:

```
Potential arbitrage opportunities detected:
[2024-03-25T12:34:56.789012] BTCUSDT: Binance 67890.1234 | CoinGecko 67550.1200 | diff 0.50%
Logged 1 opportunities to opportunities.csv
```

## Para Kazanma Stratejisi

1. **Fırsatları izleme:** Script'i 5-10 dakikalık aralıklarla çalıştırıp yüksek farkları tespit edin.
2. **Hızlı işlem:** Fark yakalandığında düşük fiyatlı borsadan alıp yüksek fiyatlı borsada satın. Ücretleri (komisyon, transfer, slipaj) mutlaka hesaba katın.
3. **Sermaye dağılımı:** Sermayenizi birkaç pariteye bölerek riski dağıtın.
4. **Kayıt tutma:** CSV çıktılarıyla hangi durumlarda kâr edildiğini analiz ederek stratejinizi iyileştirin.

## Uyarılar

- API limitleri ve gecikmeler nedeniyle fiyatlar hızla değişebilir.
- Borsalar arası transfer süreleri kârı azaltabilir; mümkün olduğunca aynı borsa içinde çapraz işlemleri tercih edin.
- Yasal gereklilikleri ve vergi yükümlülüklerini göz önünde bulundurun.

Bu otomasyon, arbitraj fırsatlarını tespit etme sürecini hızlandırarak daha bilinçli ve zamanında alım-satım kararları almanızı sağlar.
