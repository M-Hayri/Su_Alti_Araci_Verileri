1.1 /derinlik topic'inin mesaj tipi std_msgs/msg/Float32'dir. ros2 topic list aktif topic'leri gösterir. Publisher sayısı 1'dir. Subscriber sayısı çalışan node'lara göre değişir.

1.2 K = 28 olduğundan hedef frekans \(K+1=29\) Hz'dir. ros2 topic hz /derinlik komutuyla ölçülen frekans yaklaşık 29 Hz olmalıdır.

1.3 Gösterge kapatıldığında sensör çalışmaya devam eder. Çünkü iki node birbirinden bağımsızdır. Gerçek araçta bir gösterge arızalansa bile sensörün diğer sistemlere veri göndermesi devam edebilir.

1.4 İki gösterge de aynı /derinlik topic'ine abone olduğu için mesaj alır. Bu veriyi kontrolcü, veri kaydedici ve operatör ekranı dinleyebilir.

1.5 rqt_graph'ta kutular node'ları, oklar ise topic üzerinden veri akışını gösterir. Sensör derinlik verisini göstergeye ve kontrolcüye gönderir; kontrolcü de motor komutunu sensöre iletir.

1.6 Tatlı suda basınç artışı:
\[
\Delta P=\rho gh=1000\cdot9{,}81\cdot1
=9810\ \text{Pa}
\]

Deniz suyunda aynı basınç farkı:
\[
h=\frac{9810}{1025\cdot9{,}81}
\approx0{,}976\ \text{m}
\]

Deniz suyunun yoğunluğu daha yüksek olduğu için aynı basınç farkı daha küçük derinliğe karşılık gelir. Bu nedenle gerçek araçta suyun yoğunluğu hesaba katılmalıdır.
Soru 2 – Derinlik kontrolü ve acil yüzeye çıkış
2.1 \(K_p=0{,}2\) için kontrol daha yavaş tepki verir. \(K_p=1\) daha hızlı bir tepki sağlayabilir. \(K_p=5\) ise daha sert komutlara ve derinlikte dalgalanmalara neden olabilir. En uygun değer, deney sonuçlarına göre hedefe hızlı ve kararlı ulaşan değerdir. Ulaşma süreleri gerçek ölçümlerden yazılmalıdır.

2.2 Hata tam sıfır olmayabilir. Bunun nedenleri sensör gürültüsü, kontrolcü kazancı ve motor komutunun sınırlandırılmasıdır.

2.3 Trigger servisinin request kısmı boştur. Response kısmında success adlı bir boolean ve message adlı bir metin bulunur. Acil yüzeye çıkış tek seferlik bir istek-cevap işlemi olduğu için topic yerine service kullanılmıştır.

2.4 İşaret ters çevrilince kontrolcü hatayı düzeltmek yerine büyütebilir. Gerçek araçta bu durum aracın hedeften uzaklaşmasına ve tehlikeli derinliklere gitmesine neden olabilir. Simülasyon, birim testleri ve suya girmeden yapılan kontrollü testlerle bu hata yakalanabilir.

2.5 Acil mod doğru uygulanmışsa hedef 2 m olarak değiştirilse bile araç acil yüzeye çıkış modunda kalmalıdır. Güvenlik açısından normal kontrol, yalnızca açık bir devam komutuyla yeniden etkinleşmelidir.

2.6 Pozitif sephiye nedeniyle motorlar durduğunda araç yavaşça yüzeye çıkar. Bu durumda yalnızca P kontrol, motor komutu sıfıra yaklaşırken aracın hedef derinlikte kalmasını sağlayamayabilir. Kalıcı hatayı azaltmak için integral terimi eklenerek PI kontrol kullanılabilir.

