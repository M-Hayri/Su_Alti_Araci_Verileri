# Mavi Gölge Yazılım Ekibi - ROS 2 İkinci Aşama Raporu (Özet)

**Öğrenci Adı Soyadı:** Emir Sultan (`028`)  
**Çalışma Paketi:** `denizalti_egitim` | **Tarih:** 5 Kasım 2026  

---

### Kişisel Parametreler (K = 8)
* **Simülasyon Frekansı:** 9.0 Hz
* **Hedef Dalış Derinliği:** 2.60 m
* **Hedef Dönüş Açısı:** 290.0° (Alternatif: 230.0°)
* **Sephiye Hızı:** 0.13 m/s
* **Max İzinli Derinlik:** 7.00 m

---

## BÖLÜM 1: SORU 3 YANITLARI

### 3.1. rqt_graph ve Motor Karıştırıcı
* `/motor_karistirici` düğümü, kontrolcülerden gelen soyut dikey itki ve dönme komutlarını fiziksel motor kanallarına çeviren bir **Güç Dağıtıcısıdır (Actuator Mixer)**. Kontrolcüler motorların yerleşimini bilmek zorunda kalmaz, donanım soyutlaması sağlanır.

### 3.2. Su Yoğunluğu ve Basınç Hatası
* Simülatör deniz suyu ($1025\text{ kg/m}^3$), hesaplayıcı ise tatlı su ($1000\text{ kg/m}^3$) kabul ettiği için sensör derinliği yanlış hesaplar. 
* $2.60\text{ m}$'lik hedef derinlikte gerçek fiziksel derinlik **$2.537\text{ m}$**'dir. Araç hedefe ulaştığını zanneder ancak $6.34\text{ cm}$ daha sığda kalır.
* Kontrolcünün bu hatayı "görmeme" sebebi, sadece sensör çıktısına güvenmesi ve gerçek ortam yoğunluğunu bilmemesidir.

### 3.3. Açısal Hata ve En Kısa Yol (Angle Wrapping)
* Mevcut açı $20^\circ$, hedef açı $290^\circ$'dir.
* **Wrapping Olmayan İlk Kontrolcü:** Uzun yoldan $+270^\circ$ döner ($9.0\text{ saniye$).
* **Düzeltilmiş (En Kısa Yol) Kontrolcü:** $-90^\circ$ dönerek hedefe **3 saniyede** ulaşır. Dönüş süresi 3 kat kısalır; böylece zaman kaybı, enerji tüketimi ve kablo dolaşması engellenir.

### 3.4. Geç Katılan Düğümler İçin QoS
* Kontrolcü geç açıldığında hedef verisini kaçırır ve araç yüzeyde kalır. Çözüm olarak hem yayıncıda hem de abonede `TRANSIENT_LOCAL` (Latching) QoS politikası kullanılarak son mesajın bellekte tutulması sağlanmıştır.

### 3.5. Zayıf Nokta (SPOF) Analizi
* Simülatörde Watchdog (zaman aşımı) olmadığından, **`/motor_karistirici`** çöktüğünde motorlar son alınan itki değerinde kilitli kalır. Bu durum araç için **kritik tehlike** oluşturur.

### 3.6. Modülerlik
* "Önce Dön, Sonra Dal" kuralı için sadece görev yöneticisindeki 1 dosya güncellenmiş, diğer 5 düğüme dokunulmamıştır. Bu da donanım entegrasyonunu ve ekip çalışmasını kolaylaştırır.

---

## BÖLÜM 2: SORU 4 YANITLARI

### 4.1. Sephiye ve Kalıcı Durum Hatası
* Sadece $P$ kontrolcüsü ($K_i = 0$) ve yukarı yönlü $0.13\text{ m/s}$ sephiye varken, araç hedefte kalamaz ve **$0.13\text{ m/s}$'lik kalıcı durum hatası** oluşur. Araç $2.47\text{ m}$'de dengede kalır, tolerans bandına giremediği için görev **DAL** aşamasında takılır.

### 4.2. İntegral Sınırı ($K_i$) Analizi
* Sephiye kuvvetini yenmek için $K_i \cdot \text{sinir} \ge 0.13$ olmalıdır.
* $K_i = 0.05$ yetersiz kalırken, **$K_i = 0.20$** sephiyeyi dengeler, hatayı sıfırlar ve görevin başarıyla tamamlanmasını sağlar.

### 4.3. İntegral Sınırı Karşılaştırması ($1.0$ vs $1000.0$)
* $\text{sinir} = 1000.0$ yapıldığında biriken devasa enerji yüzünden araç hedefi çok fazla aşar ($>1.6\text{ m}$ aşma) ve dipteki engellere çarpma riski oluşur. Sınırın $1.0$ yapılması bu salınımları önler.

### 4.4. Watchdog ve Güvenlik
* Sensör ya da motorlar kesildiğinde Watchdog devreye girer ve motorları sıfırlar. Araç **pozitif sephiyeli** olduğu için motorlar durduğunda kendi kendine güvenli şekilde yüzeye çıkar. Negatif sephiyeli araçlarda ise bu durum dibe çökmesine yol açar.

### 4.5. Parametre Sınırları ve Defensive Programming
* Sınırları aşan değerler (örneğin $8.5\text{ m}$ derinlik) yazılımsal olarak reddedilir. Operatör hatasına güvenmek yerine bu korumaların yapılması donanımı korumak için şarttır.

### 4.6. Veri Kaydı (`ros2 bag`)
* Ham sensör verisini kaydetmek, daha sonra çevrimdışı analiz yapabilmek ve ortam yoğunluğuna göre verileri yeniden kalibre edebilmek için kritik önem taşır. Kayıt oynatılırken çakışma (race condition) olmaması için canlı düğümler kapatılmalıdır.