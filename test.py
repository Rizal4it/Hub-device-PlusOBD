import asyncio
from logging import StreamHandler

async def main():
    reader = writer = None
    try:
        # Membuka koneksi ke server
        reader, writer = await asyncio.open_connection("0.0.0.0", 50020)

        # Kirim data pertama ke server
        writer.write(bytes.fromhex("000F333533323031333530333835383833"))
        await writer.drain()

        # Menerima respons dari server
        data = await asyncio.wait_for(reader.read(2048), timeout=20)
        if not data:
            print("No data received from the server.")
            return
        print("Received data:", data)

        # Kirim data kedua ke server
        writer.write(bytes.fromhex("000000000000003608010000016B40D8EA30010000000000000000000000000000000105021503010101425E0F01F10000601A014E0000000000000000010000C7CF"))
        await writer.drain()

        # Menerima respons dari server setelah pengiriman kedua
        data = await asyncio.wait_for(reader.read(2048), timeout=20)
        if not data:
            print("No data received from the server.")
            return
        print("Received data:", data)

        # Terus menerima data dari server dalam loop
        while True:
            data = await asyncio.wait_for(reader.read(2000), timeout=30)
            if not data:
                print("No data received, closing connection.")
                return
            print("Received data:", data)

    except asyncio.TimeoutError:
        print("Connection timeout occurred.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Pastikan koneksi ditutup dengan benar jika reader dan writer valid
        if writer:
            writer.close()
            await writer.wait_closed()

# Menjalankan program utama
if __name__ == "__main__":
    asyncio.run(main())
