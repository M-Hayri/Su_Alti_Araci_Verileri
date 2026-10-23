Soru 1.1
Mesaj Tipi: Float32 türündedir, derinlik bilgisini ondalıklı sayı formatında taşır.  
Yayıncı ve Abone Durumu: Sistemde 1 adet yayıncı (derinlik_sensoru) ve 1 adet abone (derinlik_gostergesi) bulunmaktadır.  

Soru 1.2
Frekans Değerlendirmesi: Ölçülen frekans hedeflenen değerle (6 Hz) tam uyumludur.
Kararlılık: Periyot 0.16 saniye civarında stabil kalmış, sapma milisaniyenin altında gerçekleştiği için veri akışının son derece düzenli ve kararlı çalıştığı görülmüştür.   

Soru 1.3
Sensör Düğümü Etkilendi mi: Hayır, gösterge kapatıldığında sensör çalışmaya ve konuya veri göndermeye kesintisiz devam etmiştir.
Neden Etkilenmedi: ROS 2'deki gevşek bağlantı mimarisi gereği yayıncı veriyi doğrudan alıcıya değil, konuya gönderir. Bu yüzden hatta abone olup olmaması yayıncının çalışmasını etkilemez.   Gerçek Araçta Neden İşimize Yarar:Arayüz veya ekran çökse bile fiziksel sensör düğümü veri üretmeyi sürdürür. 
Kontrolcü ve otopilot kesintisiz veri almaya devam ederek aracın kontrolsüz batmasını önler.   Sistem çalışırken ana akışı kesmeden yeni telemetri veya kayıt programları bağlanabilir.

Soru 1.4 İkisi de Mesaj Alıyor mu: Evet, ikinci gösterge açıldığında iki terminal de aynı derinlik verisini eşzamanlı olarak okumuştur. 
Aynı Derinlik Verisini Dinleyen 3 Program Örneği:Derinlik Kontrolcüsü (PID): Hedef derinlikte kalmak için dikey motorlara itiş komutu hesaplayan otopilot sistemi.   Yer İstasyonu Arayüzü (GUI): Operatörün su altındaki derinliği ekranda canlı izlemesini sağlayan gösterge programı.   Güvenlik Sistemi (Failsafe): Araç izin verilen maksimum derinliği aşarsa acil yüzeye çıkışı tetikleyen koruma mekanizması.  

Soru 1.5
Şemanın Açıklaması:Düğümler (Ovallar): Sistemde bağımsız çalışan Python süreçlerini temsil eder.   Konu (Dikdörtgen Kutu): Düğümler arasındaki tek yönlü haberleşme hattıdır.   Oklar: Sensörden konuya giden ok yayıncıyı, konudan göstergeye giden ok ise aboneyi gösterir. Sisteme bağlı diğer oklar log mekanizması içindir.  

Soru 1.6
Hidrostatik Basınç: 10 metre derinlikte sadece suyun yaptığı basınç yaklaşık 100552.5 Pa (yaklaşık 1.01 bar) çıkmaktadır.   Toplam Basınç: Açık hava basıncı da eklendiğinde mutlak basınç yaklaşık 201877.5 Pa (yaklaşık 2.02 bar) olmaktadır.   Sensör Değerlendirmesi: Sensörümüz gösterge basıncı ölçmektedir (veya yüzeydeki hava basıncını sıfırlamaktadır). Çünkü yüzeydeyken derinliği 0 metre okuyoruz; mutlak basınç ölçseydi yüzeydeki açık hava basıncı yüzünden araç suya girmeden 10 metre derinde görünürdü.  

Soru 2.1
Kp Değerlerinin Karşılaştırması:Kp = 0.2: Araç çok yavaş tepki verir ve hedefe varması 20-25 saniyeyi bulur. Aşım yapmaz fakat su akıntılarına karşı yetersiz kalır.   Kp = 1.0: Araç 7-9 saniye gibi makul bir sürede hedefe ulaşır, yaklaşırken yumuşakça yavaşlar ve 2.8 metreye dengeli şekilde oturur.   Kp = 5.0: Motorları sürekli maksimum güce zorlar, hedef derinliği aşar ve hedef etrafında ileri geri salınım yaparak motorları yorar.   Seçilen Değer ve Gerekçesi: Kp = 1.0 seçilmelidir. Sistemi salınıma sokmadan ve motorları zorlamadan en kararlı sürede hedef derinliğe oturttuğu için en dengeli performansı verir.  

Soru 2.2
Simülasyondaki Durum: Dış kuvvet, sürtünme veya kaldırma kuvveti olmadığı için araç hedef derinliğe ulaştığında hata matematiksel olarak tam sıfır olmaktadır.   Gerçek Dünyada Neden Tam Sıfır Olamaz:Gerçek denizaltılar acil bir arızada batmamak için hafif pozitif sephiyeli (yüzerliği olan) tasarlanır.   Sadece P kontrolcü kullanıldığında araç tam hedefe varınca hata sıfır olur ve motor komutu da sıfırlanır.   Motor durduğu anda kaldırma kuvveti aracı yukarı iter.   Aracı derinde tutabilmek için motorun hep biraz basması, motorun basabilmesi için de sistemde sürekli küçük bir hatanın kalması gerekir.   Buna kalıcı durum hatası denir; hatayı tamamen sıfırlamak için sisteme İntegral (I) terimi eklenmelidir.

Soru 2.3
Request ve Response Açıklaması:Request (İstek): Kesikli çizgilerin üst kısmıdır ve boştur; servisi tetiklemek için dışarıdan herhangi bir ek veri göndermek gerekmez.   Response (Yanıt): Çizgilerin alt kısmıdır; işlem bitince geri dönen başarı durumunu (success) ve açıklama metnini (message) içerir.   Neden Topic Değil de Service: Topic tek yönlüdür, mesajın ulaşıp ulaşmadığını doğrulamaz. Acil yüzeye çıkış kritik bir güvenlik adımı olduğu için kontrolcünün komutu aldığından ve yüzeye yöneldiğinden kesin olarak emin olmak (onay almak) amacıyla çift yönlü servis kullanılmıştır.

Soru 2.4
İşaret Ters Çevrildiğinde Ne Oldu: Sistem negatif geri besleme yerine kararsız pozitif geri beslemeye geçti. Araç yüzeydeyken hata pozitif olmasına rağmen motor komutu ters üretildi ve dalmak yerine yüzeye itiş uyguladı; derinde olsaydı hatayı düzeltmek yerine son sürat dibe kaçmaya çalışacaktı.   Gerçek Araçta Ne Olurdu: Araç kontrolsüzce dibe dalar, gövde ezilme derinliğini aşarak basınca dayanamayıp parçalanabilir veya deniz tabanına çarpabilirdi.   Suya Girmeden Nasıl Yakalanır: Bilgisayar ortamında simülasyon testleri koşularak, atölyede pervanelerin dönüş yönü fiziksel olarak gözle kontrol edilerek ve kod içine acil durum derinlik sınırları eklenerek yakalanır. 

Soru 2.5
Mevcut Kod Ne Yapıyor: Hedef derinlik parametresini her döngüde okuduğu için, acil çıkış çağrıldıktan sonra birisi hedefi 2 metre yaparsa araç acil modu bırakıp tekrar 2 metreye dalmaya başlar.   Güvenlik Açısından Ne Yapması Gerekir: Sistem acil durum moduna kilitlenmeli ve dışarıdan gelen hedef derinlik değişikliklerini tamamen yok saymalıdır. Normal çalışmaya ancak operatör özel bir sıfırlama servisi tetiklediğinde dönmelidir.  

Soru 2.6
Gözlem: Pozitif sephiye taklit edildiğinde araç tam hedefte duramaz, hedefin biraz yukarısında asılı kalır. Çünkü araç tam hedefe geldiğinde hata sıfırlandığı için motor durur ve kaldırma kuvveti aracı tekrar yukarı çeker. Motorun aracı sabit tutacak itişi üretebilmesi için sürekli küçük bir hatanın kalması gerekir.   Çözüm: Kontrolcüye İntegral (I) terimi eklenerek sistem PI veya PID yapılmalıdır. İntegral terimi geçmiş hataları toplayarak kaldırma kuvvetini tam dengeleyecek motor komutunu üretir ve aracı tam hedef derinliğe oturtur.   