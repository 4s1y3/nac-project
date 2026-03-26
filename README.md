# NAC Sistemi — Network Access Control

RADIUS protokolü kullanılarak geliştirilmiş bir Ağ Erişim Denetimi sistemi. FreeRADIUS, FastAPI, PostgreSQL ve Redis ile Docker Compose üzerinde çalışmaktadır.

## Teknolojiler

- FreeRADIUS 3.2
- Python 3.13 / FastAPI
- PostgreSQL 18
- Redis 8
- Docker Compose

## Gereksinimler

- Docker
- Docker Compose

## Kurulum

1. Repoyu klonla:
   git clone https://github.com/4s1y3/nac-project.git
   cd nac-project

2. Ortam dosyasını oluştur:
   cp .env.example .env

3. .env dosyasını aç ve değerleri düzenle.

4. Servisleri başlat:
   docker compose up -d

5. Servislerin sağlıklı çalıştığını kontrol et:
   docker compose ps

## Servisler

| Servis      | Port      | Açıklama                        |
|-------------|-----------|----------------------------------|
| FastAPI     | 8000      | Policy Engine REST API           |
| FreeRADIUS  | 1812/udp  | RADIUS Kimlik Doğrulama          |
| FreeRADIUS  | 1813/udp  | RADIUS Accounting                |
| PostgreSQL  | 5432      | Veritabanı                       |
| Redis       | 6379      | Önbellek ve Rate Limiting        |

## API Endpoint'leri

| Endpoint         | Metot | Açıklama                        |
|------------------|-------|----------------------------------|
| /auth            | POST  | Kullanıcı kimlik doğrulama       |
| /authorize       | POST  | VLAN politika ataması            |
| /accounting      | POST  | Oturum verisi kaydetme           |
| /users           | GET   | Kullanıcı listesi ve durum       |
| /sessions/active | GET   | Aktif oturumlar (Redis)          |
| /health          | GET   | Sistem sağlık kontrolü           |

API dokümantasyonu: http://localhost:8000/docs

## Test Komutları

PAP kimlik doğrulama:
   radtest admin_user admin123 localhost 0 testing123

MAB kimlik doğrulama:
   echo "User-Name=AA:BB:CC:DD:EE:FF, User-Password=AA:BB:CC:DD:EE:FF, Calling-Station-Id=AA:BB:CC:DD:EE:FF" | radclient localhost auth testing123

Accounting Start:
   echo "User-Name=admin_user, Acct-Status-Type=Start, Acct-Session-Id=test123, NAS-IP-Address=127.0.0.1" | radclient localhost acct testing123

FastAPI sağlık kontrolü:
   curl http://localhost:8000/health

## Kullanıcı Grupları ve VLAN Atamaları

| Grup     | VLAN |
|----------|------|
| admin    | 10   |
| employee | 20   |
| guest    | 30   |

## Test Kullanıcıları

| Kullanıcı Adı | Şifre        | Grup     |
|---------------|--------------|----------|
| admin_user    | admin123     | admin    |
| employee_user | employee123  | employee |
| guest_user    | guest123     | guest    |

## Güvenlik Notları

- Şifreler bcrypt ile hash'lendi (maliyet faktörü: 12)
- Rate limiting: 5 başarısız denemede 300 saniyelik engelleme
- Hassas bilgiler .env dosyasında tutulur, Git'e gönderilmez
- Tüm servisler izole bir Docker ağında iletişim kurar