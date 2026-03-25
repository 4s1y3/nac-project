# NAC Sistemi Projesi

Bu proje, Docker Compose üzerinde FreeRADIUS + PostgreSQL + Redis + FastAPI ile tam bir NAC (Network Access Control) sistemi kurmaktadır.

## Gereksinimler

- Docker ve Docker Compose
- Python 3.13 (API için)

## Kurulum ve Çalıştırma

1. Projeyi klonlayın:
   ```bash
   git clone <repo-url>
   cd nac-project
   ```

2. `.env` dosyasını oluşturun (`.env.example`'dan kopyalayın):
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin (secret'ları ayarlayın)
   ```

3. Sistem çalıştırın:
   ```bash
   docker compose up -d
   ```

4. Servisler hazır olana kadar bekleyin (healthcheck'ler tamamlanacak).

## Test Araçları

### PAP/CHAP Authentication Testi (radtest)
```bash
# PAP testi
radtest admin_user admin123 localhost 0 testing123

# CHAP testi (eğer destekleniyorsa)
radtest chap_user chap123 localhost 0 testing123
```

### MAB Testi (radclient)
```bash
# Bilinen MAC
echo "User-Name=AA:BB:CC:DD:EE:FF, Calling-Station-Id=AA:BB:CC:DD:EE:FF" | radclient localhost auth testing123

# Bilinmeyen MAC (reject)
echo "User-Name=FF:FF:FF:FF:FF:FF, Calling-Station-Id=FF:FF:FF:FF:FF:FF" | radclient localhost auth testing123
```

### Accounting Testi (radclient)
```bash
# Start
echo "User-Name=admin_user, Acct-Status-Type=Start, Acct-Session-Id=12345, NAS-IP-Address=192.168.1.1" | radclient localhost acct testing123

# Interim-Update
echo "User-Name=admin_user, Acct-Status-Type=Interim-Update, Acct-Session-Id=12345, Acct-Session-Time=60, Acct-Input-Octets=1000, Acct-Output-Octets=2000" | radclient localhost acct testing123

# Stop
echo "User-Name=admin_user, Acct-Status-Type=Stop, Acct-Session-Id=12345, Acct-Session-Time=120, Acct-Input-Octets=2000, Acct-Output-Octets=4000, Acct-Terminate-Cause=User-Request" | radclient localhost acct testing123
```

### FastAPI Endpoint Testleri (curl)
```bash
# Health check
curl http://localhost:8000/health

# Auth (PAP)
curl -X POST http://localhost:8000/auth -H "Content-Type: application/json" -d '{"username": "admin_user", "password": "admin123"}'

# Auth (MAB)
curl -X POST http://localhost:8000/auth -H "Content-Type: application/json" -d '{"calling_station_id": "AA:BB:CC:DD:EE:FF", "method": "MAB"}'

# Authorize
curl -X POST http://localhost:8000/authorize -H "Content-Type: application/json" -d '{"username": "admin_user"}'

# Accounting
curl -X POST http://localhost:8000/accounting -H "Content-Type: application/json" -d '{"username": "admin_user", "session_id": "12345", "status_type": "Start", "nas_ip": "192.168.1.1"}'

# Users
curl http://localhost:8000/users

# Sessions
curl http://localhost:8000/sessions/active
```

## Mimari

- **FreeRADIUS**: RADIUS sunucusu (auth, authz, acct)
- **PostgreSQL**: Kullanıcı ve accounting verisi
- **Redis**: Oturum cache ve rate-limit
- **FastAPI**: Policy engine (rlm_rest entegrasyonu)

## Notlar

- Tüm servisler healthcheck ile korunmuştur.
- Environment variable'lar `.env` dosyasında saklanır.
- Test kullanıcıları: admin_user (admin), employee_user (employee), guest_user (guest)
- VLAN grupları: admin (VLAN 10), employee (VLAN 20), guest (VLAN 30)
```

## Mimari

- **FreeRADIUS**: RADIUS sunucusu (auth, authz, acct)
- **PostgreSQL**: Kullanıcı ve accounting verisi
- **Redis**: Oturum cache ve rate-limit
- **FastAPI**: Policy engine (rlm_rest entegrasyonu)

## Notlar

- Tüm servisler healthcheck ile korunmuştur.
- Environment variable'lar `.env` dosyasında saklanır.
- Test kullanıcıları: admin_user (admin), employee_user (employee), guest_user (guest)
- VLAN grupları: admin (VLAN 10), employee (VLAN 20), guest (VLAN 30)
```

---

## 🚀 Projeyi Çalıştırma Adımları

1. **Hazırlık**:
   - .env dosyasını oluştur (.env.example'dan kopyala ve değerleri doldur, örneğin `POSTGRES_PASSWORD=your_password`).

2. **Çalıştır**:
   ```bash
   cd /home/elifasiye/nac-project
   docker-compose up -d
   ```

3. **Bekle**: Servisler healthcheck tamamlanana kadar (1-2 dakika).

4. **Test Et**:
   - API: `curl http://localhost:8000/health` ({"status": "ok", "db": true, "redis": true})
   - RADIUS: Yukarıdaki `radtest`/`radclient` komutlarını çalıştır.

5. **Durdur**:
   ```bash
   docker-compose down

   ```

