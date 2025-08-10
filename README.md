"""
# Google Sheets Belge Yöneticisi

Kendi Google Service Account credentials'ınızı kullanarak Google Sheets verilerinizi okuyun, işleyin ve yönetin.

## 🌟 Özellikler

- **Dinamik Credentials**: Kendi Service Account JSON'ınızı kullanın
- **Tek Spreadsheet İşleme**: Belirli bir spreadsheet'i işleyin
- **Folder İşleme**: Tüm folder'daki spreadsheet'leri toplu işleyin
- **Belge Yönetimi**: İşlenmiş belgeleri kaydedin ve yönetin
- **Gelişmiş Arama**: Belge içeriğinde detaylı arama
- **İçerik Analizi**: Kelime frekansı ve istatistikler

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
# Repository'yi klonlayın
git clone <repo-url>
cd google-sheets-document-manager

# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Google Service Account Kurulumu

1. **Google Cloud Console'a gidin**: https://console.cloud.google.com
2. **Proje oluşturun** veya mevcut projeyi seçin
3. **API'leri etkinleştirin**:
   - Google Sheets API
   - Google Drive API
4. **Service Account oluşturun**:
   - IAM & Admin > Service Accounts
   - "Create Service Account" tıklayın
   - Gerekli bilgileri girin
5. **JSON Key indirin**:
   - Service Account'a tıklayın
   - Keys > Add Key > Create new key > JSON
   - Dosyayı indirin ve içeriğini kopyalayın
6. **Spreadsheet'leri paylaşın**:
   - Service Account email'ini kopyalayın
   - Spreadsheet'lerinizi bu email ile paylaşın (Viewer yeterli)

### 3. Uygulamayı Çalıştırın
```bash
streamlit run main.py
```

## 📁 Proje Yapısı

```
├── main.py                           # Ana uygulama
├── shared/
│   ├── config.py                    # Yapılandırma ve geçici dosya yönetimi
│   └── protocol.py                  # Base sınıflar ve veri modelleri
├── core/
│   ├── document_processor.py        # Belge işleme ve chunking
│   ├── document_manager.py          # Belge kaydetme/yükleme
│   └── credentials_manager.py       # Credentials doğrulama
├── readers/
│   └── dynamic_google_sheets_reader.py  # Dinamik Google Sheets okuyucu
├── interface/
│   └── enhanced_streamlit_app.py    # Gelişmiş Streamlit arayüzü
├── documents/                       # İşlenmiş belge içerikleri
├── metadata/                        # Belge metadata'ları
├── temp_credentials/                # Geçici credentials dosyaları
└── requirements.txt                 # Python bağımlılıkları
```

## 🎯 Kullanım

### Credentials Girişi
1. Uygulamayı açın
2. Service Account JSON içeriğini yapıştırın
3. (Opsiyonel) Google Drive Folder ID'sini girin
4. "Test Et" ile doğrulayın
5. "Kaydet ve Devam Et" ile uygulamayı başlatın

### Tek Spreadsheet İşleme
1. Sidebar'dan Spreadsheet ID veya URL'sini girin
2. "Bilgi Al" ile detayları görün
3. "İşle & Kaydet" ile belgeleri işleyin

### Folder İşleme
1. Setup sırasında Folder ID girdiyseniz folder sekmesi aktif olur
2. Folder'daki tüm spreadsheet'leri görüntüleyin
3. Seçili olanları veya tümünü işleyin

### Arama ve Analiz
1. "Arama" sekmesinden belge içeriğinde arama yapın
2. "Belgeler" sekmesinden kayıtlı belgeleri görüntüleyin
3. Belge detaylarında içerik analizi yapın

## 🔧 Teknik Detaylar

- **Chunk Boyutu**: 1024 karakter (özelleştirilebilir)
- **Chunk Overlap**: 100 karakter
- **Desteklenen Formatlar**: Google Sheets
- **Depolama**: Yerel dosya sistemi (JSON + TXT)
- **Güvenlik**: Geçici credentials otomatik temizlenir

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
"""