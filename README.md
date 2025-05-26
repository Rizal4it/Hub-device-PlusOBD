
# 🚗 Teltonika OBD-II Data Parser with Codec8e (FMB920)

Proyek ini bertujuan untuk **mengambil data kendaraan dari perangkat Teltonika FMB920**, memprosesnya melalui **parsing Codec8 Extended (8E)**, dan mengirimkannya ke **MQTT server** dalam format JSON. Data yang digunakan mencakup parameter GPS, data sensor kendaraan dari OBD-II, serta informasi status kendaraan lainnya.

---

##  Arsitektur System
Untuk pengalaman interaktif penuh, silakan buka aplikasi di browser Anda:
[Buka Aplikasi Interaktif Sistem](https://g.co/gemini/share/421ddba040f0)



## 🔧 Fitur Utama

- ✅ **Parsing protokol Teltonika Codec8/Codec8e**
- ✅ **Validasi CRC16-ARC** sebelum memproses data
- ✅ Ekstraksi data **GPS**, **OBD-II**, dan **IO**
- ✅ Konversi data menjadi format **JSON**
- ✅ Publish ke **MQTT Broker**
- ✅ Struktur modular dengan `controller`, `service`, `parser`, `utils`

---

## 📂 Struktur Folder

```bash
.
├── index.py                  # Entry point TCP server
├── teltonika_server.py       # TCP socket listener untuk perangkat
├── controller/
│   └── teltonika_controller.py
├── service/
│   └── teltonika_service.py
├── parser/
│   ├── codec8.py             # Parser untuk Codec8
│   ├── codec8e.py            # Parser untuk Codec8 Extended
│   └── model_json.py         # Mapping data AVL ke JSON
├── utils/
│   └── crc.py                # Implementasi CRC16-ARC
├── config.py                 # Konfigurasi MQTT dan setting lain
├── mqtt.py                   # Koneksi dan publisher MQTT
├── test.py                   # Tes lokal untuk payload dummy
````

---

## ⚙️ Teknologi & Tools

* **Python 3.10+**
* **asyncio** untuk TCP server
* **paho-mqtt** untuk koneksi MQTT
* **Teltonika FMB920** sebagai perangkat utama
* **OBD-II Emulator / kendaraan asli** untuk sumber data

---

## 🚀 Cara Menjalankan

1. **Install dependensi** (gunakan virtualenv jika perlu):

   ```bash
   pip install -r requirements.txt
   ```

2. **Sesuaikan konfigurasi di `config.py`**:

   * Port listener Teltonika (default: 5027)
   * MQTT broker host dan topik

3. **Jalankan TCP Server**:

   ```bash
   python3 index.py
   ```

4. **Lihat log data masuk dan hasil parsing** di terminal.

---

## 📊 Contoh Output (JSON)

```json
{
  "imei": "350612079568265",
  "timestamp": "2025-05-26T08:01:03+00:00",
  "latitude": -7.734585,
  "longitude": 110.3776683,
  "engine_rpm": 850,
  "vehicle_speed": 0,
  "fuel_level": 0,
  "coolant_temp": 74,
  ...
}
```

---

## 📘 Catatan Penting

* Beberapa parameter OBD hanya tersedia jika:

  * ECU kendaraan mendukung PID-nya
  * Dongle OBD berkualitas dan kompatibel
* Emulator seperti **Freematics** bisa digunakan untuk pengujian

---

## 📚 Referensi

* [Teltonika Codec8/8E Protocol](https://wiki.teltonika-gps.com/)
* [FMB920 Parameter IO List](https://wiki.teltonika-gps.com/view/FMB920_Teltonika_Data_Sending_Parameters_ID)
* [CRC16-ARC Spec](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat-bits.16)

---

## 👨‍💻 Kontributor

* 🧑 Haffian Naufal Afrizal
* 🙌 Mas Geryx (kontributor parsing & MQTT)
* 💼 Pembimbing Magang

---

## 📝 Lisensi

Proyek ini menggunakan lisensi MIT. Silakan digunakan untuk keperluan edukasi dan riset.
