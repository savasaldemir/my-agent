# 🤖 My Agent - Universal AI Software Engineering Agent

> Hangi IDE'de çalışırsanız çalışın, hangi işletim sistemine sahip olursanız olun - **My Agent** her yerde yanınız.

## 📋 Özet

**My Agent**, tüm programlama dillerinde çalışabilen, IDE-agnostic bir AI yazılım mühendisliği ajanıdır. Kodunuzu analiz eder, hataları düzeltir, features ekler ve production-ready uygulamalar oluşturmaya yardımcı olur.

### ✨ Temel Özellikler

- 🌐 **Polyglot Support**: Python, JavaScript/TypeScript, Go, Java, Rust, C++, C#, PHP, Ruby, Swift, Dart, vb.
- 💻 **Cross-Platform**: Windows, macOS, Linux, BSD
- 🔌 **IDE Integration**: VS Code, JetBrains IDEs, Neovim, Vim, Emacs, Sublime Text
- 📱 **Multi-Target**: Web, Desktop (Electron), Mobile (React Native), Embedded Systems
- 🏗️ **Architecture Support**: Monolitik, Microservices, Serverless
- 🔐 **Enterprise Ready**: Authentication, Authorization, Security Scanning, Compliance
- 📊 **Full Stack**: Frontend, Backend, Database, DevOps, Testing, Documentation
- 🚀 **Production Ready**: Out-of-the-box deployment configurations

## 🎯 Hedefler

1. **Kod Analizi**: Mevcut projeyi derinlemesine analiz et
2. **Akıllı Hata Düzeltme**: Bug'ları otomatik tespit ve düzelt
3. **Feature Geliştirme**: Yeni özellikler ekle
4. **Refactoring**: Kodu iyileştir
5. **Testing**: Otomatik test üret
6. **Documentation**: Dökümentasyon oluştur
7. **DevOps**: Deployment yapılandırması hazırla

## 📦 Teknoloji Stack

### Backend
- **Python 3.11+** - Core AI Logic
- **Node.js 18+** - API Gateway, Microservices
- **Go 1.21+** - High-performance Workers
- **FastAPI** - Python Web Framework
- **Express.js** - Node.js Framework
- **PostgreSQL** - Primary Database
- **Redis** - Caching, Queue Management
- **MongoDB** - Document Storage

### Frontend
- **React 18** - Web UI
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **Electron** - Desktop App
- **React Native** - Mobile App

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Local Development
- **Kubernetes** - Production Orchestration
- **GitHub Actions** - CI/CD
- **Prometheus + Grafana** - Monitoring

### IDE Plugins
- **VS Code Extension API** - VS Code Plugin
- **IntelliJ Plugin SDK** - JetBrains IDEs
- **Neovim Plugin API** - Neovim Integration

## 🚀 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 18+
- Go 1.21+
- Docker & Docker Compose
- Git

### Hızlı Başlangıç

```bash
# Repository'i klonla
git clone https://github.com/savasaldemir/my-agent.git
cd my-agent

# Altyapı servislerini tek komutla başlat (PostgreSQL + Redis + MongoDB)
npm run dev

# Backend bağımlılıkları
cd backend/core
python -m pip install -r requirements.txt
cd ../..

# Core API'yi başlat
python -m uvicorn backend.core.app:app --host 0.0.0.0 --port 8000

# Başka terminalde API Gateway
cd backend/api-gateway
npm install
npm run dev

# Başka terminalde Web UI
cd frontend/web
npm install
npm run dev
```

Servis URL'leri:

- Core API: `http://localhost:8000`
- API Gateway: `http://localhost:3000`
- Web UI: `http://localhost:5173`

Altyapıyı durdurmak için:

```bash
npm run dev:stop
```

## ✅ Tek Komut Ortam Hazirlama (Windows)

Makinede eksik runtime'lari kontrol edip (gerekirse kurup) backend + gateway + frontend bagimliliklarini hazirlamak icin:

```bash
powershell -ExecutionPolicy Bypass -File scripts/bootstrap-local.ps1 -AutoInstallRuntimes
```

Sadece backend odakli (UI kurulumuna dokunmadan) hazirlik icin:

```bash
powershell -ExecutionPolicy Bypass -File scripts/bootstrap-local.ps1 -AutoInstallRuntimes -BackendOnly
```

Mevcut backend venv kullaniliyorsa script `pip install` adimini atlar.
Zorla yeniden kurulum icin:

```bash
powershell -ExecutionPolicy Bypass -File scripts/bootstrap-local.ps1 -AutoInstallRuntimes -BackendOnly -ForcePythonDeps
```

Altyapiyi da otomatik kaldirmak icin:

```bash
powershell -ExecutionPolicy Bypass -File scripts/bootstrap-local.ps1 -AutoInstallRuntimes -StartInfra
```

Sadece on kontrol (preflight) icin:

```bash
powershell -ExecutionPolicy Bypass -File scripts/preflight.ps1
```

Not: Bootstrap scripti, hizli ve uyumlu kurulum icin oncelikle `backend/core/requirements.local.txt`
dosyasini kullanir. Bu dosya yoksa `backend/core/requirements.txt` ile devam eder.

## 🗃️ Veritabanı Migration (Alembic)

Core klasöründen çalıştır:

```bash
cd backend/core

# Mevcut migration'ları uygula
alembic upgrade head

# Yeni migration oluştur (autogenerate)
alembic revision --autogenerate -m "your_migration_message"

# Son migration'ı geri al
alembic downgrade -1
```

## 📚 Proje Yapısı

```
my-agent/
├── backend/                  # Backend Services
│   ├── core/                # Python Core Engine
│   ├── services/            # Node.js/Go Microservices
│   ├── api-gateway/         # API Gateway
│   └── workers/             # Task Workers
├── frontend/                # Frontend Applications
│   ├── web/                # React Web App
│   ├── desktop/            # Electron Desktop
│   └── mobile/             # React Native
├── plugins/                # IDE Extensions
├── sdk/                    # Multi-language SDKs
├── daemon/                 # System Daemon
├── cli/                    # Command Line Interface
├── tests/                  # Test Suites
├── docs/                   # Documentation
└── deployment/             # Deployment Configs
```

## 🔧 Kullanım

### Uygulama Giris Noktalari

Bu depoda iki ayri uygulama vardir:

1. `AGENT`: Modern web arayuzlu ana uygulama
2. `fabrika_Agent`: Masaustu kontrol merkezi + legacy yerel fabrika arayuzu

AGENT uygulamasini tek komutla calistirmak icin:

```bash
python launch_agent.py
```

Bu komut:

- backend/core API'yi baslatir
- backend/api-gateway uygulamasini baslatir
- frontend/web build artefaktlarini gateway uzerinden servis eder
- tarayicida `http://127.0.0.1:3000` adresini acar

Fabrika kontrol merkezini baslatmak icin:

```bash
python fabrika_Agent/launch_fabrika.py
```

Bu arayuz ile:

- AGENT stack'i baslatabilirsiniz
- AGENT web UI'yi acabilirsiniz
- legacy `yerel_fabrika_gui.py` uygulamasini ayri olarak acabilirsiniz
- baska proje klasorlerini workspace'e alip intake calistirabilirsiniz
- internet gerektiren isleri kuyruklayip daha sonra devam ettirebilirsiniz

### Var Olan Projeyi Iceri Alma (Intake)

Farkli dil ve veritabani kullanan mevcut bir projeyi tek komutla tarayip profil cikarabilirsiniz:

```bash
npm run project:intake -- -ProjectPath "C:\\path\\to\\your-project"
```

Bu komut hedef projede `.agent-intake/` klasoru olusturur ve su dosyalari uretir:

- `project-profile.json` (dil dagilimi, birincil dil, veritabani sinyalleri)
- `security-findings.json` (hizli guvenlik bulgulari)
- `intake-report.md` (oncelikli iyilestirme ozeti)

Not: Varsayilan olarak `fabrika_Agent` klasoru intake taramasindan dislanir.
Isterseniz ek dislama klasorleri verebilirsiniz:

```bash
powershell -ExecutionPolicy Bypass -File scripts/project-intake.ps1 -ProjectPath "." -ExtraExcludeDirs "fabrika_Agent","frontend"
```

Bu raporla birlikte agent'e su tip komutlar verebilirsiniz:

- "bu projeyi intake raporuna gore guvenlik acisindan harden et"
- "high severity bulgulari kapat ve testleri yesile cek"
- "mimariyi bozmadan kodu daha okunur ve production-ready yap"

### CLI ile Kullanım

```bash
# Yeni proje analizi
my-agent analyze ./my-project

# Otomatik bug fix
my-agent fix ./my-project

# Test çalıştır
my-agent test ./my-project

# Deployment yap
my-agent deploy ./my-project --target docker
```

### Web Dashboard

- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: (System credential)

### IDE Plugin

- **VS Code**: "My Agent" uzantısını kur marketplace'ten
- **JetBrains**: Plugin'i kur IDE ayarlarından
- **Neovim**: `:MyAgentSetup` komutunu çalıştır

## 🎓 Öğrenme Kaynakları

- [Architecture Guide](./docs/architecture.md)
- [API Documentation](./docs/api.md)
- [Plugin Development](./docs/plugin-development.md)
- [Deployment Guide](./docs/deployment.md)

## 🤝 Katkıda Bulunma

Projeye katkı sağlamak istiyorsan:

1. Fork yap
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit at (`git commit -m 'Add amazing feature'`)
4. Push et (`git push origin feature/amazing-feature`)
5. Pull Request aç

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bak.

## 📞 İletişim

- 📧 Email: contact@myagent.dev
- 🐦 Twitter: @myagent
- 💬 Discord: [My Agent Community](https://discord.gg/myagent)
- 📖 Website: https://myagent.dev

---

**Version**: 1.0.0-alpha  
**Last Updated**: 2026-07-08  
**Status**: 🚀 In Active Development
