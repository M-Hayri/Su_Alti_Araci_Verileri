# CEVAPLAR.md - Mavi Gölge ROS 2 Derinlik Kontrolü ve Düğüm Analizi Raporu

---
		 **K = 1**
## 1. Düğüm ve Konu (Node / Topic) Grafiği Analizi

Sistem çalışırken `rqt_graph` aracı ile elde edilen düğüm ve konu yapısı aşağıda sunulmuştur:

![RQT Graph](rqt_graph.png)

### 1.1 Grafikteki Düğümler (Nodes) Nelerdir ve Görevleri Nedir?
* **/derinlik_sensoru:**
 Derinlik sensörü simülasyonunu çalıştıran düğümdür. Aracın su altındaki anlık derinlik verisini ölçer/üretir ve sistemdeki diğer düğümlerin kullanabilmesi için /derinlik konusuna yayınlar.

* **/derinlik_kontrolcu:**
 Derinlik kontrolünü sağlayan PID kontrolcü düğümüdür. Sensörden gelen anlık derinlik verisini alır, hedef derinlik ile karşılaştırarak hata değerini hesaplar ve motorlara iletilmek üzere /motor_komutu konusuna kumanda sinyallerini yayınlar.




### 1.2 Grafikteki Konular (Topics) Nelerdir ve Ne İşe Yarar?
/derinlik
/motor_komutu
/parameter_events
/rosout
	* **/derinlik:**
 Sensör düğümü (/derinlik_sensoru) tarafından üretilen anlık derinlik verisinin kontrolcü düğümüne (/derinlik_kontrolcu) iletildiği veri konusudur.

	* **/motor_komutu:**
 Kontrolcü düğümünün hesapladığı PID kumanda/itki sinyallerinin motor sürücülerine aktarıldığı veri konusudur.

        * **/derinlik/data:** 
Sensör sürücüsü ile kontrolcü düğümü arasında köprü görevi gören veri yoludur. Sürücü düğümü ölçtüğü anlık derinlik değerini (örneğin 2.5 metre) bu konunun içerisine bir mesaj olarak yazar. Kontrolcü düğümü de bu konudan veriyi okuyarak aracın nerede olduğunu anlar.


### 1.3 Düğümler Arasındaki İletişim Mantığı Nasıl İşler?
* ROS 2 mimarisinde bu iletişim **Yayıncı - Abone (Publisher - Subscriber)** modeliyle gerçekleşir.

#ros2 topic info /derinlik
Type: std_msgs/msg/Float32
Publisher count: 1
Subscription count: 1

#ros2 topic info /motor_komutu
Type: std_msgs/msg/Float32
Publisher count: 1
Subscription count: 1



* `/derinlik_surucu` düğümü bir **Yayıncı (Publisher)** gibi davranarak anlık derinlik verisini kesintisiz ve sürekli bir şekilde `/derinlik/data` konusuna basar.
* `/derinlik_kontrolcu` düğümü ise bir **Abone (Subscriber)** olarak bu konuyu sürekli dinler. 
* Bu iletişim yapısı asenkron (tek yönlü ve sürekli) bir veri akışıdır; sürücü düğümü veriyi gönderir, kontrolcünün alıp almadığını beklemeden bir sonraki veriyi yayınlamaya devam eder.

### 1.4 Servis Yapısı (Services) Nasıl Analiz Edilir?
 * **1. Komut Çalıştırma ve Mesaj Alma Durumu:**
`ros2 run denizalti_egitim derinlik_gostergesi --ros-args -r __node:=gosterge2` komutu çalıştırıldığında:
* **Evet, ikisi de mesaj alır.** İki farklı isimdeki gösterge düğümü (`/derinlik_gostergesi` ve `/gosterge2`) aynı `/derinlik` konusuna (topic) abone (subscriber) olurlar.
* ROS 2 Yayıncı-Abone (Publisher-Subscriber) mimarisinde bir konudan yayınlanan veri, o konuyu dinleyen tüm abonelere (subscriber) bağımsız ve eşzamanlı olarak ulaştırılır.

**2. Araçta Aynı Derinlik Verisini Dinlemesi Gereken Program Örnekleri (3 Örnek):**
1. **Derinlik Kontrolcüsü (PID / Otopilot Düğümü):** Aracın istenen hedef derinlikte kalabilmesi için motorlara itki/kumanda sinyali üreten ana kontrol düğümü.
2. **Gösterge ve Yer Kontrol İstasyonu (GUI / RQT Visualizer):** Operatörün aracı anlık olarak izleyebilmesi için derinlik verisini ekrana basan arayüz düğümü.
3. **Veri Kayıt ve Kara Kutu Düğümü (ROS 2 Bag Reader / Logger):** Görev sonrası analiz, güvenlik denetimi veya arıza tespiti yapılabilmesi için tüm derinlik verilerini veritabanına/disk dosyasına kaydeden düğüm.


* Sistemde acil durumlar için tanımlanan `/acil_yuzey` servisi `std_srvs/srv/Trigger` yapısındadır.
* Konuların (Topics) aksine servisler **İstek - Yanıt (Request - Response)** mantığıyla senkron çalışır. 
* Bir acil durum anında istemci (örneğin bir operatör veya güvenlik modülü) bu servise bir istek gönderir. Kontrolcü düğümü bu isteği aldığı an mevcut hedefini derhal `0.0 metre` (yüzey) yapar, motorlara tam güç yüzeye çıkma emri verir ve istemciye "Acil yüzeye çıkış başlatıldı" şeklinde bir onay yanıtı (Response) döner.

### 1.5 Parametre Yönetimi (ROS 2 Parameters) Nasıl Çalışır?


* 1.RQT Graph Düğüm (Node / Kutu) Analizi

    /derinlik_sensoru: Denizaltının anlık derinliğini hesaplayan veya simüle eden veri kaynağı düğümdür.

    /derinlik_kontrolcu: Sensörden gelen mevcut derinlik ile belirlenen hedef derinliği kıyaslayan ve motorlara gerekli itki komutunu üreten mantıksal kontrolör düğümüdür.

    /derinlik_gostergesi: Sistemdeki anlık derinlik verisini operatörün görsel olarak takip edebilmesi için ekrana basan arayüz düğümüdür.

* 2. RQT Graph Konu (Topic / Ok) Analizi

    /derinlik Oku: /derinlik_sensoru düğümünden çıkan bu ok, sensörün bir Publisher (Yayıncı) olduğunu gösterir. Okun /derinlik_kontrolcu ve /derinlik_gostergesi düğümlerine gitmesi ise bu iki düğümün Subscriber (Abone) sıfatıyla anlık derinlik verisini eşzamanlı olarak dinlediğini ifade eder.

    /motor_komutu Oku: /derinlik_kontrolcu düğümünden çıkan ok, kontrolcünün hesapladığı PID komut sinyallerini motor sürücü sistemine aktaran yayın hattıdır.


* ROS 2 Parameter yapısı, düğümler çalışırken kodun içindeki değişkenleri dışarıdan değiştirmemize olanak tanır.
* Bizim sistemimizde hedef derinlik (örneğin 5 metreden 2 metreye inmek) veya PID kontrolcünün hassasiyet katsayıları (`Kp`, `Ki`, `Kd`) kod durdurulup tekrar derlenmeden, çalışma zamanında (runtime) `ros2 param set` komutu ile dinamik olarak güncellenebilir.

### 1.6 Sistem Akışının Genel Değerlendirmesi


	tatlı su(p=1000lg/m^3 , g = 9.81 m/s^2) 1 m derinlkikte su basıncı kac Pa artar?
	 P = basınc
	 P = p . g .h
	 P = 1000 x 9.81 x 1  =  9810 Pa (9.81 kPa) 

	Deniz suyu => p(deniz) = 1025 kg/m^3
	9810 = 1025 x 9.81 x h(deniz) yaklasik=0.9756 m 

Özkütle Farkı: Deniz suyunun özkütlesi (p = 1025 kg/m^3), içerdiği tuz miktarından dolayı tatlı sudan (p = 1000 kg/m^3) daha yüksektir. 

Ölçüm Sapması: Bar30 gibi basınç sensörleri doğrudan derinliği değil, üzerlerindeki hidrostatik basıncı ölçerler. Yazılımdaki dönüşüm algoritması tatlı suya göre ayarlanırsa, araç denize girdiğinde daha sığ bir derinlikte daha yüksek basınç okuyacaktır. 

Görev Güvenliği ve Seyir Hassasiyeti: Araç denizde 0.975 m derinlikteyken sensör kendisini 1.000 m derinlikte sanır (yaklaşık %2.4 hata). Otonom görevlerde, dibe yakın seyirlerde veya hassas havuz/deniz görevlerinde bu sapma aracın tabana çarpmasına veya hedef derinliği yanlış tutmasına neden olur. Bu yüzden yazılımdaki özkütle(p)  parametresinin ortam şartlarına göre güncellenmesi kritiktir. 




## 2. Derinlik Kontrolü ve Parametre Analizi

### 2.1 Kp Analizi ve Seçimi
* **Kp = 0.2 (Aşırı Sönümlü Tepki):** Oransal kazanç düşük olduğu için sistemin ürettiği kontrol sinyali zayıftır. Araç hedefe çok yavaş ulaşır (yükselme süresi uzundur). Sistemde aşım (overshoot) oluşmaz ancak hedefe oturması çok zaman alır.
* **Kp = 1.0 (Optimum Tepki):** Araç hedefe dengeli, kararlı ve hızlı bir şekilde ulaşır. Yükselme süresi makuldür, sistemde yok denecek kadar az bir aşım meydana gelir ve araç kısa sürede hedef derinlikte kararlı hale geçer.
* **Kp = 5.0 (Yetersiz Sönümlü / Kararsız Tepki):** Oransal kazanç çok yüksek olduğu için sistem küçük hatalara bile çok büyük tepkiler verir. Araç hedefe çok hızlı yaklaşır fakat hedef noktayı aşarak etrafında şiddetli salınımlar yapmaya başlar ve sistem kararsızlaşır.
* **Seçim ve Gerekçe:** **Kp = 1.0** değeri seçilmelidir. Çünkü sistem tepki süresi (hız) ile sistem kararlılığı (salınımsızlık) arasındaki en ideal dengeyi bu katsayı sağlar.

![Kp 0.2](kanit/kp_02.png)
![Kp 1.0](kanit/kp_10.png)
![Kp 5.0](kanit/kp_50.png)

---

### 2.2 Kalıcı Durum Hatası (Steady-State Error) Analizi
Gözlem: Sadece Oransal (P) kontrolör kullanıldığında, araç hedef derinliğe yaklaştıkça hata küçülür, dolayısıyla motorlara giden güç emri de (K_p x hata) gittikçe azalır. 

Nedeni: Tam hedef noktasına ulaşıldığında hata teorik olarak sıfır olur. Ancak gerçek dünyada suyun direnci, aracın kendi ağırlığı veya sürtünme gibi dış etkenler nedeniyle motorların ürettiği çok küçük güç bu dirençleri yenmeye yetmez. Bu yüzden araç hedef değerin çok az altında veya üstünde kalarak durur, hata tam olarak sıfırlanmaz (küçük bir sapma payı kalır).

### 2.3 `std_srvs/srv/Trigger` Çıktısı ve Service Kullanım Sebebi
#### ros2 interface show std_srvs/srv/Trigger Komut Çıktısı:
```text
---
bool success   # indicate successful run of triggered service
string message # informational, e.g. for error messages

İstek (Request) ve Yanıt (Response) Kısımları:
--- çizgisinin üstü İstek (Request) kısmıdır ve boştur. Çağıran taraf ekstra bir parametre göndermeden servisi tetikler. 
  --- çizgisinin altı Yanıt (Response) kısmıdır. İşlem tamamlandığında servisin başarılı olup olmadığını belirten success ve açıklama metni içeren message bilgisini geri döndürür. 
 
 Topic Yerine Service Kullanma Sebebi:
    Konular (Topics) sürekli ve tek yönlü veri akışı sağlar; gönderilen mesajın karşıya ulaşıp ulaşmadığı teyit edilmez. 
      Acil yüzeye çıkış ise kritik bir güvenlik adımıdır. Service yapısı Soru-Cevap (İstek-Yanıt) mantığıyla çalıştığı için komutun iletildiğinden ve aracın yüzeye çıkış moduna geçtiğinden kesin olarak emin olunmasını (onay alınmasını) sağlar.   



2.4 Kontrolcü İşaretinin Ters Çevrilmesi
 Gözlem (İşaret Ters Çevrilince):
Kontrol denkleminde komut işareti ters çevrildiğinde ($\text{komut} = -K_p hata), araç hedef derinliğe gitmek yerine hedeften hızla uzaklaşmıştır. 
  Araç yüzeyde ise ve hedef 2m yapıldıysa, araç yüzeyden yukarı çıkmaya (veya motorları zorlamaya) çalışmıştır.Araç hedefin altındaysa, aracı aşağı bastırarak hatanın kontrolden çıkıp daha da büyümesine neden olmuştur.Gerçek Araçta Olası Sonuçlar:Araç hedef derinliğe inmek yerine yüzeye çarpabilir veya tabana son sürat çarparak fiziksel hasar alabilir.
  Motorlar sürekli maksimum güçte çalışmak zorunda kalarak aşırı ısınabilir veya yanabilir.Suya Girmeden Bu Hatayı Yakalama Yöntemleri:
  Yazılımsal Test / Sanal Ortam: Kod havuza veya denize girmeden önce bilgisayar ortamındaki testlerle (yaptığımız sahte sensör gibi) çalıştırılarak motor yönü izlenir.Kod İçi Kontrol Testleri: Kontrol fonksiyonuna yapay bir hata değeri verilip üretilen çıktının doğru yönde olup olmadığı test edilir.Masaüstü Testi: Araç karadayken sensöre elle veya yazılımla yapay derinlik verisi verilir ve motorların doğru yöne dönüp dönmediği gözle denetlenir.


2.5 Acil Yüzeye Çıkış Sırasında Parametre Değişimi

    Mevcut Kodun Davranışı:
Acil yüzeye çıkış servisi (/acil_yuzey) çağrıldıktan sonra dışarıdan biri ros2 param set /derinlik_kontrolcu hedef_derinlik 2.0 komutunu çalıştırırsa, kontrolcü yeni hedefi okur ve aracı tekrar  2 m derinliğe daldırmaya çalışır. 
Güvenlik Açısından Yapılması Gereken:
Güvenlik Kilidi: Acil yüzey servisi tetiklendiğinde kontrolcü içerisinde "acil durum aktif" bilgisi tutulmalıdır.
Parametre Engelleme: Acil durum aktif olduğu sürece dışarıdan komutla hedef derinlik değiştirilse bile kontrolcü bu yeni değeri kabul etmemeli ve hedefi 0.0 m'de tutmaya devam etmelidir.  
 Sıfırlama / Devam Servisi: Araç güvenli bir şekilde yüzeye çıktıktan sonra sistemin tekrar normale dönmesi için ayrı bir /devam (veya /reset) servisi çağrılmadığı sürece yeni hedef talepleri işleme alınmamalıdır.


2.6 Pozitif Sephiye (Pozitif Yüzebilirlik) Etkisi ve Çözümü
  Gözlem ve Analiz:
Sensör düğümüne aracın kendiliğinden yüzeye çıkma eğilimini taklit eden bir yapı eklendiğinde:   Araç hedef derinliğe yaklaştıkça hata ufalır.  
 Hata küçüldükçe kontrolcünün motorlara verdiği güç (K_p x hata )azalır.   Belli bir derinlikte motorun aşağı doğru ürettiği itme gücü, suyun aracı yukarı ittiği güçle eşitlenir.Sonuç olarak araç hedef derinliğe tam ulaşamadan hedefin biraz üstünde takılı kalır; tam hedefte duramaz (kalıcı bir pay/sapma oluşur). 
   Çözüm (Ne Eklenedebilir?):İntegral (I) Terimi Eklemek / PID Kontrol: Sisteme bir İntegral (K_i) kontrolör eklenmelidir.  
    Mantık: İntegral yapısı, aracın hedefte duramadığı her an oluşan küçük hataları zamanla üst üste toplayarak büyütür. Bu sayede motor komutu zamanla artar ve suyun yukarı itme gücünü yenerek aracın tam hedef derinlikte (0 cm hata ile) durmasını sağlar.




  **Ne sordum ne ogrendim**

 Parametre Yönetimi ve Tip Duyarlılığı

    Ne Sordum? ros2 param get /derinlik_kontrolcu Kp komutunu çalıştırdığımda neden Parameter not set hatası aldığımı sordum.

    Ne Öğrendim? ROS 2 parametre isimlerinin büyük-küçük harfe duyarlı (case-sensitive) olduğunu öğrendim. ros2 param list çıktısındaki gibi Kp yerine kp yazmam gerektiğini ve ROS 2 düğümlerinin çalışma zamanında (runtime) sistem kapatılmadan parametre güncelleyebilme esnekliğini kavradım.



Basınç ve Fiziksel Çevre Dönüşümü

    Ne Sordum? Bar30 sensörünün tatlı su ve deniz suyunda ürettiği basınç farklarının derinlik hesaplamasına etkisini ve neden farklılık gösterdiğini sordum.

    Ne Öğrendim?  Deniz suyunun özkütlesi tatlı sudan daha yüksek olduğu için, tatlı suya göre kalibre edilmiş bir yazılımın denizde aracı daha derin/sığ sanarak sapma yapacağını ve otonom görevlerde özkütle değerinin yazılımsal olarak güncellenmesinin önemini öğrendim



Haberleşme Mimarisi: Topic vs Service

   Ne Sordum? Acil yüzeye çıkış protokolünde neden verilerin yayınlandığı bir Topic yerine Service kullanmamız gerektiğini sordum.
   Ne Öğrendim? Topic yapısının yayınla-unut (publish-subscribe) mantığıyla çalışan asenkron bir hat olduğunu ve mesajın ulaşıp ulaşmadığını garantilemediğini öğrendim. Service yapısının ise İstek-Yanıt (Request-Response) mantığıyla çalışarak komutun kontrolcüye ulaştığını ve acil yüzey moduna geçildiğini kesin teyit (acknowledgement) ile garanti altına aldığını öğrendim. 



P Kontrol Sınırları ve Sephiye Etkisi

    Ne Sordum? Pozitif sephiyeli (yüzme eğilimi olan) bir araçta sadece Oransal (P) kontrolör kullanıldığında aracın neden hedefte tam duramadığını ve bunu nasıl çözeceğimi sordum.

   Ne Öğrendim? P kontrolcüde araç hedefe yaklaştıkça hatanın ve dolayısıyla üretilen komutun (Kp x hata) küçüldüğünü, suyun yukarı itme kuvvetiyle motor gücünün bir noktada eşitlenip kalıcı sapma (steady-state error) oluşturduğunu öğrendim. Bu sorunu çözmek için geçmiş hataları biriktirerek motor komutunu zamanla artıran İntegral (I) teriminin (PID) sisteme eklenmesi gerektiğini kavradım



RQT Graph ve Düğüm İletişim Analizi

    Ne Sordum? RQT Graph üzerindeki kutuların (düğümler) ve okların (konular/topics) ne anlama geldiğini kendi cümlelerimle nasıl açıklayabileceğimi sordum.

    Ne Öğrendim? Kutuların bağımsız çalışan yazılım parçaları (node), okların ise verinin aktarıldığı tek yönlü kanallar (topic) olduğunu öğrendim. Okun çıkış yaptığı düğümün Yayıncı (Publisher), okun gittiği düğümlerin ise Abone (Subscriber) olduğunu ve tek bir sensör verisinin aynı anda hem kontrolcü hem de gösterge tarafından dinlenebileceğini kavradım.



PID K_p Grafikleri ve Sistem Tepkisi
    Ne Sordum? K_p = 0.2, 1.0 ve 5.0 değerlerinde aldığım rqt_plot grafiklerini gösterip sistemin verdiğin tepkileri yorumlamasını istedim

Ne Öğrendim? K_p değeri düşükken (0.2) sistemin hantal kaldığını ve hedefe geç ulaştığını, aşırı yüksekken (5.0) sistemin kararsızlığa girip sürekli hedefi aşarak şiddetli salınım (overshoot) yaptığını, K_p = 1.0 civarında ise sistemin hızlı ve dengeli bir şekilde kararlı hale geldiğini öğrendim.



Ters Kontrolcü ve Güvenlik Testleri 
    Ne Sordum? Kontrol denkleminde komut işaretini bilerek ters çevirdiğimde (komut = -K_p x hata) sistemin neden hedeften uzaklaştığını ve gerçek araçta ne gibi tehlikeler yaratacağını sordum.  

    Ne Öğrendim? İşaret ters olunca hatanın pozitif beslemeli bir şekilde çığ gibi büyüdüğünü, aracın hedeften uzaklaşıp tabana veya yüzeye çarpma riski doğduğunu öğrendim. Bu tür fiziksel kaza risklerini suya girmeden önce masaüstü testleri (dry-run) ve sanal simülasyonlarla yakalamanın şart olduğunu kavradım.



    
    
    
    
    
    
    
    

