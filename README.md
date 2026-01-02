Bu uygulama, modern **GTK4** ve **Libadwaita** kütüphanelerini kullanan, Debian ve Pardus tabanlı sistemler için optimize edilmiş şık ve fonksiyonel bir Flatpak yönetim aracıdır.

---

# Flatpak Yönetim Merkezi: Modern ve Güçlü 

**Neden?**, Linux masaüstünüzde yüklü olan Flatpak uygulamalarını uçbirime (terminale) ihtiyaç duymadan, görsel ve kullanıcı dostu bir arayüzle yönetmenizi sağlayan yeni nesil bir araçtır. Özellikle Pardus ve Debian 13 "Trixie" gibi modern dağıtımların tasarım diline tam uyum sağlayacak şekilde geliştirilmiştir.

## Öne Çıkan Temel Özellikler

### 1. Akıllı Uygulama Takibi ve Görsel Arayüz

* **Otomatik Listeleme:** Sisteminizde yüklü olan tüm Flatpak uygulamalarını anında tespit eder ve kolay erişim için bir açılır listede sunar.
* **Detaylı Bilgi Kartı:** Seçilen uygulamanın diskte kapladığı boyutu ve uygulama ikonunu dinamik olarak görüntüler.
* **Libadwaita Tasarımı:** Modern "Dark Mode" (Karanlık Mod) desteği ve adaptif tasarımı sayesinde her ekran boyutunda kusursuz görünür.

### 2. Gelişmiş Uygulama Yönetimi

Uygulama üzerinden sadece tek bir tıklama ile şu işlemleri yapabilirsiniz:

* **Hızlı Kurulum:** Flathub üzerinden uygulama kimliğini (App ID) yazarak saniyeler içinde kurulum başlatın.
* **Güncelleme:** Mevcut uygulamalarınızı tek tek veya toplu olarak en son sürüme yükseltin.
* **Güvenli Kaldırma:** Standart kaldırma işleminin yanı sıra, uygulama kalıntılarını temizleyen **"Tamamen Sil"** (Delete Data) seçeneğiyle sisteminizi temiz tutun.

### 3. Veri Güvenliği: Yedekleme ve Geri Yükleme

Flatpak Yönetim Merkezi, diğer yönetim araçlarından farklı olarak uygulama verilerinizi korumaya odaklanır:

* **Ayarları Yedekle:** Uygulamanıza ait tüm kişisel ayarları ve verileri (`.var/app` altındaki dosyaları) tek tıkla Masaüstünüze sıkıştırılmış bir arşiv (`.tar.gz`) olarak yedekler.
* **Geri Yükle:** Yeni bir sisteme geçtiğinizde veya verileriniz bozulduğunda, Masaüstündeki yedeği otomatik olarak bularak ayarlarınızı eski haline getirir.

### 4. Tek Tıkla Sistem Bakımı: "Süper Temizlik"

Sisteminizi optimize etmek için karmaşık komutlar ezberlemenize gerek yok. Uygulama içerisinde yer alan **"Süper Temizlik ve Onarım"** butonu:

* Tüm uygulamaları günceller.
* Kullanılmayan artık paketleri (unused runtimes) temizler.
* Olası dosya hatalarını tamir eder (`flatpak repair`).

---

## Teknik Özellikler ve Uyumluluk

* **Dil:** Python 3
* **Arayüz:** GTK4 & Libadwaita 1.0+
* **Hedef Platform:** Pardus, Debian 13, GNOME 45+ masaüstü ortamları.
* **Güvenlik:** Arka planda işlemleri asenkron (threading) yürüterek donmaları önler ve sistem kaynaklarını verimli kullanır.

## Neden Flatpak Pro?

Eğer terminal kullanmaktan çekiniyor veya Flatpak uygulamalarınızın ayarlarını manuel olarak yedeklemekle vakit kaybetmek istemiyorsanız, **Flatpak Yönetim Merkezi** sizin için en ideal çözümdür. Modern, hızlı ve güvenilir bir yönetim deneyimi sunar.

---

**İpucu:** Uygulamayı çalıştırmak için sisteminizde `python3-gi`, `libadwaita-1-dev` ve `flatpak` paketlerinin kurulu olduğundan emin olun.
