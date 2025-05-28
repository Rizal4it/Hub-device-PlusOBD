# Teltonika GPS Server

This project is a Python-based TCP server designed to receive and process GPS data from Teltonika devices (such as the FMB920 model), supporting **Codec 8 and Codec 8 Extended** protocols. Its primary function is to parse incoming raw data—including GPS coordinates, vehicle speed, OBD-II sensor readings (such as fuel levels and engine diagnostics), and vehicle status information—then convert it into a structured **JSON format**. The processed data is subsequently published to an **MQTT server**, enabling real-time vehicle tracking and monitoring. The system ensures efficient data handling, seamless integration with IoT platforms, and reliable transmission for fleet management or telematics applications. Built for scalability, it serves as a bridge between Teltonika tracking devices and modern data analytics pipelines.
## 🔧 Features

- **TCP Server**: Handles multiple simultaneous connections from Teltonika GPS devices
- **Protocol Support**: Codec 8 and Codec 8 Extended (8E) parsing
- **MQTT Integration**: Publishes parsed GPS data to MQTT broker
- **Data Validation**: CRC verification and data integrity checks
- **OBD Parameters**: Supports extensive OBD-II parameter mapping
- **Async Processing**: Built with asyncio for high performance
- **Configurable**: Environment-based configuration management

## 🏗️  Architecture System
``` mermaid
graph TB
    %% Physical Layer
    subgraph "Vehicle & Sensors"
        Vehicle[🚗 Vehicle]
        OBD_Port[📟 OBD Port]
        OBD_Dongle[🔌 OBD Dongle<br/>Bluetooth Interface]
        GPS_Sat[🛰️ GPS Satellites]
        GSM_Tower[📡 GSM Tower]
    end

    %% FMB920 Device
    subgraph "FMB920 Teltonika Device"
        GPS_Module[📍 GPS Module<br/>- Latitude/Longitude<br/>- Speed, Altitude<br/>- Satellites count]
        BT_Module[📶 Bluetooth Module<br/>OBD Data Reception]
        GSM_Module[📱 GSM Module<br/>TCP Communication]
        Data_Collector[🔄 Data Collector<br/>- Combines GPS + OBD<br/>- Internal sensors<br/>- Codec 8/8E format]
    end

    %% Configuration
    subgraph "Device Configuration"
        Configurator[⚙️ Teltonika Configurator<br/>- Server IP & Port<br/>- OBD parameters<br/>- Send intervals<br/>- Codec format]
    end

    %% Server Infrastructure
    subgraph "Server Infrastructure"
        TCP_Server[🖥️ TCP Server<br/>teltonika_server.py<br/>Port: Custom]
        
        subgraph "Data Processing Pipeline"
            IMEI_Handler[🆔 IMEI Handler<br/>- Receive 15 bytes<br/>- Send ACK 0x01]
            AVL_Receiver[📥 AVL Data Receiver<br/>- Receive packets<br/>- Send ACK count]
            CRC_Validator[✅ CRC Validator<br/>Data integrity check]
            Parser[🔍 Codec 8E Parser<br/>codec8e.py<br/>- Extract GPS data<br/>- Extract OBD data<br/>- Extract IO data]
            JSON_Converter[🔄 JSON Converter<br/>model_json.py<br/>Format standardization]
        end
        
        MQTT_Client[📡 MQTT Client<br/>config/mqtt.py<br/>Publisher]
    end

    %% MQTT Broker
    subgraph "MQTT Infrastructure"
        MQTT_Broker[🔄 MQTT Broker<br/>mqtt.iot-db.geryx.space:50000<br/>Topic: topic/data]
    end

    %% Flutter App
    subgraph "Flutter Application"
        App_MQTT[📱 MQTT Subscriber<br/>MQTTController]
        Data_Display[📊 Real-time Dashboard<br/>DataPage]
    end

    %% Data Flow Connections with Numbers
    Vehicle -->|1| OBD_Port
    OBD_Port -->|2| OBD_Dongle
    OBD_Dongle -->|3 Bluetooth| BT_Module
    GPS_Sat -->|4| GPS_Module
    GSM_Tower -->|5| GSM_Module
    
    %% FMB920 Internal Flow
    BT_Module -->|6| Data_Collector
    GPS_Module -->|7| Data_Collector
    GSM_Module -->|8| Data_Collector
    
    %% Configuration Flow
    Configurator -.->|0 Configure| Data_Collector
    
    %% TCP Communication Flow
    Data_Collector -->|9 TCP Connection| TCP_Server
    TCP_Server -->|10| IMEI_Handler
    IMEI_Handler -->|11 ACK 0x01| Data_Collector
    Data_Collector -->|12 AVL Data Packet| AVL_Receiver
    AVL_Receiver -->|13| CRC_Validator
    CRC_Validator -->|14| Parser
    Parser -->|15| JSON_Converter
    JSON_Converter -->|16| MQTT_Client
    AVL_Receiver -->|17 ACK Data Count| Data_Collector
    
    %% MQTT Flow
    MQTT_Client -->|18 Publish JSON| MQTT_Broker
    MQTT_Broker -->|19 Subscribe| App_MQTT
    App_MQTT -->|20| Data_Display

    %% Communication Sequence Details
    subgraph "Communication Steps"
        Step1[9 FMB920 connects to TCP Server]
        Step2[10 Server handles connection]
        Step3[11 IMEI Exchange 15 bytes + ACK]
        Step4[12 AVL Data transmission]
        Step5[13 CRC Validation]
        Step6[14 Binary data parsing]
        Step7[15 JSON conversion]
        Step8[16 MQTT preparation]
        Step9[17 Send ACK to device]
        Step10[18 Publish to MQTT broker]
        Step11[19 Flutter app subscribes]
        Step12[20 Display real-time data]
        
        Step1 --> Step2 --> Step3 --> Step4 --> Step5
        Step5 --> Step6 --> Step7 --> Step8
        Step4 --> Step9
        Step8 --> Step10 --> Step11 --> Step12
    end

    %% Data Sources with Numbers
    subgraph "Data Collection Sources"
        Source1[1 Vehicle OBD Data<br/>Engine parameters]
        Source2[2 Bluetooth Communication<br/>OBD dongle to FMB920]
        Source3[3 GPS Positioning<br/>Location & movement data]
        Source4[4 Internal Sensors<br/>Accelerometer etc]
        
        Source1 --> Source2 --> Data_Collector
        Source3 --> Data_Collector
        Source4 --> Data_Collector
    end

    %% Data Format Details
    subgraph "Data Formats and Standards"
        TCP_Format[AVL Data Packet Structure<br/>1 Preamble 4 bytes<br/>2 Length 4 bytes<br/>3 Codec ID 1 byte<br/>4 Data Count 1 byte<br/>5 AVL Data Records<br/>6 CRC 4 bytes]
        
        JSON_Format[JSON Output Structure<br/>1 imei: 350612079568265<br/>2 timestamp: 2025-05-26T08:01:03<br/>3 latitude: -7.734585<br/>4 longitude: 110.3776683<br/>5 data_payload object]
        
        OBD_Params[OBD Parameters Collected<br/>1 Engine RPM IO ID 36<br/>2 Vehicle Speed IO ID 24<br/>3 Coolant Temp IO ID 72<br/>4 Fuel Level IO ID 9<br/>5 Engine Load IO ID 52<br/>6 Throttle Position IO ID 17<br/>7 Plus 25+ more parameters]
    end

    Parser --> TCP_Format
    JSON_Converter --> JSON_Format
    BT_Module --> OBD_Params

    %% Processing Pipeline Details
    subgraph "Server Processing Pipeline"
        Process1[1 Device Registration<br/>IMEI validation & handshake]
        Process2[2 Data Reception<br/>AVL packet buffering]
        Process3[3 Data Validation<br/>CRC check & format validation]
        Process4[4 Binary Parsing<br/>Codec 8E decoding]
        Process5[5 Data Structuring<br/>GPS + OBD + IO organization]
        Process6[6 JSON Formatting<br/>Standardized output format]
        Process7[7 MQTT Publishing<br/>Real-time data distribution]
        Process8[8 Client Updates<br/>Flutter app receives data]
        
        Process1 --> Process2 --> Process3 --> Process4
        Process4 --> Process5 --> Process6 --> Process7 --> Process8
    end

    IMEI_Handler --> Process1

    %% Styling
    classDef physicalLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef deviceLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serverLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef mqttLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef appLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef formatLayer fill:#f1f8e9,stroke:#33691e,stroke-width:1px
    classDef processLayer fill:#e3f2fd,stroke:#0d47a1,stroke-width:1px

    class Vehicle,OBD_Port,OBD_Dongle,GPS_Sat,GSM_Tower physicalLayer
    class GPS_Module,BT_Module,GSM_Module,Data_Collector,Configurator deviceLayer
    class TCP_Server,IMEI_Handler,AVL_Receiver,CRC_Validator,Parser,JSON_Converter,MQTT_Client serverLayer
    class MQTT_Broker mqttLayer
    class App_MQTT,Data_Display appLayer
    class TCP_Format,JSON_Format,OBD_Params formatLayer
    class Step1,Step2,Step3,Step4,Step5,Step6,Step7,Step8,Step9,Step10,Step11,Step12,Process1,Process2,Process3,Process4,Process5,Process6,Process7,Process8,Source1,Source2,Source3,Source4 processLayer
```

### Data Flow

1. Data Collection (Steps 1-8)
  
    - Vehicle Data: 
    The system retrieves vehicle diagnostic data through the OBD port (1).
    - Bluetooth Communication: OBD dongle transmits data to FMB920 via Bluetooth (2-3)
    - GPS Positioning: FMB920 receives location data from GPS satellites (4)
    - GSM Connection: GSM module connects the device to the cellular network (5)
    - Data Aggregation: The Data Collector in FMB920 aggregates all data (GPS, OBD, internal sensors) in Codec 8E format (6-8).

2. Server Communication (Steps 9-17)

    - TCP Connection: FMB920 initiates a TCP connection to the server (9)
    - Device Registration: Server receives IMEI (15 bytes) and sends ACK (10-11)
    - Data Transmission: Device sends AVL data packets to the server (12)
    - Data Processing: Server validates CRC, parses binary data, and converts to JSON (13-15)
    - MQTT Preparation: JSON data is prepared for MQTT publication (16)
Acknowledgment: The server sends confirmation of the amount of data received (17)

3. Data Distribution (Steps 18-20)

    - MQTT Publishing: Server publishes JSON data to MQTT broker (18)
    - Client Subscription: Flutter application subscribes to MQTT topic (19)
    - Real-time Display: Data is displayed on the application dashboard in real-time (20)

### 📂 Project Structure

```
├── config/
│   ├── config.py           # Configuration management
│   ├── mqtt.py            # MQTT connector and publishing
│   └── teltonika_server.py # TCP server initialization
├── controller/
│   └── teltonika_server.py # Main TCP connection handler
├── service/
│   └── teltonika_server.py # Business logic and data processing
├── parser/
│   ├── codec8.py          # Codec 8 protocol parser
│   ├── codec8e.py         # Codec 8 Extended protocol parser
│   └── model_json.py      # Data mapping and transformation
├── utils/
│   └── crc.py             # CRC16-ARC verification utilities
├── index.py               # Main application entry point
├── test.py                # Client simulation for testing
└── .env                   # Environment configuration
```


---

## ⚙️ Technology & Tools

### Core Technologies
- **Python 3.8+** - Main programming language
- **asyncio** - Asynchronous TCP server dan concurrent processing
- **aiomqtt** - Modern MQTT client dengan async support
- **python-dotenv** - Environment variable management

### Hardware & Protocols
- **Teltonika FMB920** - Primary GPS tracking device
- **OBD-II Interface** - Vehicle diagnostic data source
- **Codec8/8E Protocol** - Teltonika binary communication protocol

### Development Tools
- **Virtual Environment** - Isolated Python environment
- **Environment Configuration** - `.env` based configuration
- **Modular Architecture** - Clean code separation

---

## 🚀 How to launch the system

### 1. Persiapan Environment

```bash
# Clone atau download project
git clone <repository-url>
cd teltonika-gps-server

# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install aiomqtt python-dotenv
```

### 3. Konfigurasi Environment

Buat file `.env` di root project:

```env
# TCP Server Configuration
TCP_SERVER_HOST=0.0.0.0
TCP_SERVER_PORT=50000

# MQTT Broker Configuration
MQTT_HOST=localhost
MQTT_PORT=1883
```

### 4. Jalankan Server

```bash
# Jalankan server utama
python index.py

# Atau untuk development dengan logging detail
python -u index.py | tee server.log
```

### 5. Testing dengan Simulator

```bash
# Jalankan test client untuk simulasi device
python test.py
```

---

## 📊 Example of Data Output

### Basic GPS Data (Codec 8)

```json
{
  "imei": "353201350385883",
  "timestamp": "2025-05-28T08:01:03+00:00",
  "latitude": -7.734585,
  "longitude": 110.3776683,
  "altitude": 120,
  "angle": 180,
  "speed": 65,
  "satellites": 12,
  "battery_voltage": 12500,
  "fuel_level": 75,
  "operate_status": true,
  "gsm_signal": 4
}
```

### Extended OBD-II Data (Codec 8E)

```json
{
  "imei": "353201350385883",
  "timestamp": "2025-05-28T08:01:03+00:00",
  "latitude": -7.734585,
  "longitude": 110.3776683,
  "altitude": 120,
  "angle": 180,
  "speed": 65,
  "satellites": 12,
  
  // Engine Parameters
  "engine_rpm": 2150,
  "vehicle_speed": 65,
  "engine_load": 45,
  "coolant_temp": 87,
  "throttle_position": 25,
  "fuel_pressure": 350,
  "intake_air_temp": 32,
  
  // Fuel & Economy
  "fuel_level": 75,
  "fuel_rate": 8.5,
  "total_odometer": 125430,
  "fuel_used_gps": 12.3,
  
  // Electrical System
  "battery_voltage": 12500,
  "power_input": 13800,
  "control_module_voltage": 12400,
  
  // Diagnostic Data
  "number_of_dtc": 0,
  "distance_traveled_mil_on": 0,
  "time_run_with_mil_on": 0,
  
  // IO Data Structure
  "io_data": [
    {
      "1B": [
        {"io_id": 1, "value": 1},
        {"io_id": 21, "value": 4}
      ]
    },
    {
      "2B": [
        {"io_id": 66, "value": 13800},
        {"io_id": 67, "value": 12500}
      ]
    }
  ],
  
  // Raw AVL Data
  "data_payload": {
    // Original parsed data structure
  }
}
```

---

## 🔍 Supported Data Parameters

### 📍 GPS & Location Data
- **Latitude/Longitude** - Koordinat GPS presisi tinggi
- **Altitude** - Ketinggian dari permukaan laut (meter)
- **Speed** - Kecepatan kendaraan (km/h)
- **Angle** - Arah kendaraan (derajat)
- **Satellites** - Jumlah satelit GPS yang terhubung

### 🚗 Vehicle Basic Data
- **IMEI** - Identifikasi unik perangkat
- **Timestamp** - Waktu data GPS (UTC)
- **Battery Voltage** - Tegangan baterai kendaraan
- **GSM Signal** - Kekuatan sinyal seluler
- **Digital Input/Output** - Status input/output digital

### 🔧 OBD-II Engine Parameters
| Parameter | IO ID | Deskripsi |
|-----------|-------|-----------|
| Engine RPM | 36 | Putaran mesin (RPM) |
| Vehicle Speed | 37 | Kecepatan kendaraan dari ECU |
| Engine Load | 31 | Beban mesin (%) |
| Coolant Temperature | 32 | Suhu pendingin mesin (°C) |
| Throttle Position | 41 | Posisi throttle (%) |
| Fuel Pressure | 34 | Tekanan bahan bakar |
| Intake Air Temperature | 39 | Suhu udara masuk (°C) |
| MAF (Mass Air Flow) | 40 | Aliran udara massa |
| Fuel Level | 9 | Level bahan bakar |
| Total Odometer | 16 | Total jarak tempuh |

### 🔋 Electrical & Control
| Parameter | IO ID | Deskripsi |
|-----------|-------|-----------|
| Battery Voltage | 67 | Tegangan baterai (mV) |
| Power Input | 66 | Input daya (mV) |
| Control Module Voltage | 51 | Tegangan modul kontrol |

### 🛠️ Diagnostic Data
| Parameter | IO ID | Deskripsi |
|-----------|-------|-----------|
| Number of DTC | 30 | Jumlah kode error |
| Distance Since Codes Clear | 49 | Jarak sejak error dihapus |
| Time Run with MIL On | 54 | Waktu MIL menyala |
| Fuel Type | 759 | Jenis bahan bakar |

---

## 🔒 Protocol Support

### Codec 8 - Standard Protocol
- **Data Structure**: Fixed 26-byte AVL record
- **IO Elements**: Basic 1B, 2B, 4B, 8B support
- **Features**: 
  - GPS coordinates dan timestamp
  - Basic vehicle parameters
  - Standard IO elements
  - CRC16-ARC verification

### Codec 8 Extended (8E) - Advanced Protocol
- **Data Structure**: Variable-length AVL records
- **IO Elements**: Extended 1B, 2B, 4B, 8B + NX support
- **Features**:
  - Full OBD-II parameter support
  - Extended IO element capacity
  - Variable-length data (NX format)
  - Enhanced error detection
  - Support for complex vehicle diagnostics

---

## 📡 MQTT Integration

### Connection Configuration
```python
# Environment variables
MQTT_HOST=localhost          # MQTT broker hostname
MQTT_PORT=1883              # MQTT broker port
```

### Publishing Details
- **Topic**: `topic/data`
- **Format**: JSON array dengan multiple records
- **QoS**: Default (0) - dapat dikonfigurasi
- **Retain**: False
- **Connection**: Persistent dengan auto-reconnect

### Message Structure
```json
[
  {
    "imei": "device_identifier",
    "timestamp": "ISO_8601_format",
    // ... GPS data
    // ... OBD parameters
    // ... IO elements
    "data_payload": { /* raw_avl_data */ }
  }
]
```

---

## ✅ Data Validation & Quality

### CRC16-ARC Verification
```python
# Implementasi CRC16-ARC dengan polynomial 0xA001
async def verify_crc(data: bytes, expected_crc: int) -> bool:
    calculated_crc = await compute_crc(data)
    return calculated_crc == expected_crc
```

### GPS Data Validation
- **Invalid Coordinates**: Filter (0.0, 0.0) sebagai invalid
- **Timestamp Validation**: Reject future timestamps
- **Range Validation**: Koordinat dalam range valid
- **Satellite Count**: Minimum satellite requirement

### Data Integrity Checks
- **Packet Length**: Verify data packet completeness
- **Protocol Compliance**: Ensure codec format adherence
- **IO Element Validation**: Validate IO data structure
- **Error Handling**: Graceful handling of malformed data

---

## 🎛️ Configuration Management

### Environment Configuration
```env
# Server Configuration
TCP_SERVER_HOST=0.0.0.0      # Bind address (0.0.0.0 for all interfaces)
TCP_SERVER_PORT=50000        # TCP listening port

# MQTT Configuration
MQTT_HOST=localhost          # MQTT broker hostname/IP
MQTT_PORT=1883              # MQTT broker port
```

### Runtime Configuration
```python
class Config:
    TCP_SERVER_HOST = os.getenv("TCP_SERVER_HOST", "0.0.0.0")
    TCP_SERVER_PORT = int(os.getenv("TCP_SERVER_PORT", "50000"))
    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
```

---

## 🔧 Development & Testing

### Testing dengan Simulator
```bash
# Jalankan test client
python test.py

# Test akan mengirim:
# 1. IMEI authentication
# 2. Sample Codec 8 data
# 3. Verify ACK response
```

### Development Guidelines

#### Menambah Parser Baru
1. Buat file parser di `parser/new_codec.py`
2. Implement parsing logic sesuai protocol
3. Update service layer untuk handle codec baru
4. Add protocol detection di main handler

#### Menambah Parameter OBD
1. Update `model_json.py` dengan mapping baru
2. Tambahkan IO ID mapping untuk parameter
3. Update dokumentasi parameter
4. Test dengan device yang support parameter

### Performance Monitoring
```python
# MQTT publish timing
start_time = time.time()
await self.client.publish(topic, payload)
end_time = time.time()
print(f"Time taken to publish: {end_time - start_time} seconds")
```

---

## 🚨 Troubleshooting Guide

### Connection Issues

**Problem**: Device tidak bisa connect ke server
```bash
# Check if server is running
netstat -an | grep :50000

# Check firewall
sudo ufw status
sudo ufw allow 50000
```

**Problem**: MQTT publishing gagal
```bash
# Test MQTT broker connectivity
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t topic/data
```

### Data Issues

**Problem**: Data parsing error
- Verify device sending correct protocol (Codec 8/8E)
- Check CRC calculation dengan hex dump
- Validate data packet length

**Problem**: Missing OBD parameters
- Ensure vehicle ECU supports requested PIDs
- Check OBD dongle compatibility
- Verify IO ID mapping dalam device configuration

### Performance Issues

**Problem**: High latency atau dropped connections
- Monitor server resource usage
- Check network connectivity stability
- Optimize async processing dengan connection pooling

---

## 📈 Performance Considerations

### Server Performance
- **Async Architecture**: Handle multiple connections efficiently
- **Memory Management**: Proper cleanup of connection resources
- **Connection Pooling**: Reuse connections untuk multiple devices
- **Error Recovery**: Graceful handling of connection failures

### Data Processing
- **Batch Processing**: Group multiple records untuk MQTT publishing
- **Data Validation**: Filter invalid data early dalam pipeline
- **CRC Verification**: Optimize CRC calculation untuk high-throughput
- **JSON Serialization**: Efficient data structure conversion

### MQTT Performance
- **Connection Persistence**: Maintain persistent MQTT connection
- **Publish Batching**: Send multiple records dalam single message
- **QoS Optimization**: Choose appropriate QoS level
- **Topic Structure**: Optimize topic naming untuk routing

---

## 🔐 Security Considerations

### Network Security
- **IP Whitelisting**: Restrict connections dari known devices
- **Port Security**: Use non-standard ports untuk production
- **SSL/TLS**: Implement encrypted communication
- **VPN Access**: Secure remote access untuk management

### Data Security
- **Data Encryption**: Encrypt sensitive vehicle data
- **Authentication**: Implement device authentication beyond IMEI
- **Access Control**: Role-based access untuk MQTT topics
- **Audit Logging**: Log all device connections dan data transfers

---

## 📚 References and Documentation

### Official Documentation
- [Teltonika Codec8/8E Protocol](https://wiki.teltonika-gps.com/view/Codec) - Protocol specification
- [FMB920 Parameter List](https://wiki.teltonika-gps.com/view/FMB920_Teltonika_Data_Sending_Parameters_ID) - Complete IO parameter list
- [OBD-II PIDs](https://en.wikipedia.org/wiki/OBD-II_PIDs) - Standard OBD parameter reference

### Technical References
- [CRC16-ARC Specification](https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat-bits.16) - CRC calculation details
- [MQTT Protocol](https://mqtt.org/mqtt-specification/) - MQTT protocol specification
- [Python asyncio](https://docs.python.org/3/library/asyncio.html) - Async programming guide

### Testing & Simulation
- [OBD-II Emulators](https://www.freematics.com/products/freematics-obd-ii-emulator/) - Hardware untuk testing
- [MQTT Clients](http://mqttfx.jensd.de/) - MQTT testing tools
- [Teltonika Configurator](https://wiki.teltonika-gps.com/view/Teltonika_Configurator) - Device configuration tool

---

## 👨‍💻 Development Team

### Core Team
- 🧑 **Afrizal** - Data Processing & Automation
- 🙌 **Mas Geryx** - Parser Development & MQTT Integration  
- 💼 **Mas Fachri** - Project Supervisor & Technical Guidance

### Kontribusi
- **Architecture Design** - Modular system design dengan separation of concerns
- **Protocol Implementation** - Complete Codec8/8E parsing implementation
- **Performance Optimization** - Async processing dan connection management
- **Documentation** - Comprehensive documentation dan testing guides


---

## 📝 MIT License

```
Copyright (c) 2025 Afrizal

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

Internship Project Notice:
This software was developed as part of a mandatory internship project. The copyright holder acknowledges that the work fulfills academic or professional training requirements.

Standard MIT Terms:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

**Penggunaan untuk keperluan edukasi dan riset sangat dianjurkan!**


---
**⭐ Jika project ini membantu, jangan lupa berikan star di GitHub! ⭐**

Made with ❤️ for the IoT 
