#include <Arduino.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();


// ==================================================
// CONFIG
// ==================================================

static const uint8_t HEADER = 0xAA;

// W = 0, H = 0
// => FLUSH / ACK 요청
static const uint16_t FLUSH_W = 0;
static const uint16_t FLUSH_H = 0;

static const uint16_t TFT_W = 480;
static const uint16_t TFT_H = 320;

static const uint16_t TILE_MAX = 16;

static const uint32_t BAUD = 1500000;


// ==================================================
// TILE BUFFER
// ==================================================

uint16_t tileBuf[TILE_MAX * TILE_MAX];


// ==================================================
// FAST RECEIVE
// ==================================================

bool readExact(uint8_t *buffer, uint16_t length)
{
    uint16_t received = 0;

    unsigned long lastData = millis();

    while (received < length)
    {
        int available = Serial.available();

        if (available > 0)
        {
            uint16_t remaining = length - received;

            if (available > remaining)
                available = remaining;

            int n = Serial.readBytes(
                buffer + received,
                available
            );

            if (n > 0)
            {
                received += n;
                lastData = millis();
            }
        }
        else
        {
            if (millis() - lastData > 1000)
                return false;

            yield();
        }
    }

    return true;
}


// ==================================================
// SETUP
// ==================================================

void setup()
{
    Serial.begin(BAUD);

    // Stream timeout
    Serial.setTimeout(1000);

    delay(100);

    // TFT
    tft.init();
    tft.setRotation(1);

    // RGB565 byte order
    tft.setSwapBytes(false);

    tft.fillScreen(TFT_BLACK);


    // UART garbage 제거
    while (Serial.available())
        Serial.read();


    // READY
    Serial.write('R');
}


// ==================================================
// LOOP
// ==================================================

void loop()
{
    // ------------------------------------------------
    // HEADER 탐색
    // ------------------------------------------------

    if (!Serial.available())
    {
        yield();
        return;
    }

    uint8_t c = Serial.read();

    if (c != HEADER)
        return;


    // ------------------------------------------------
    // PACKET HEADER
    // ------------------------------------------------

    uint8_t packet[8];

    if (!readExact(packet, 8))
        return;


    // ------------------------------------------------
    // BIG ENDIAN decode
    // ------------------------------------------------

    uint16_t x =
        ((uint16_t)packet[0] << 8) |
        packet[1];

    uint16_t y =
        ((uint16_t)packet[2] << 8) |
        packet[3];

    uint16_t w =
        ((uint16_t)packet[4] << 8) |
        packet[5];

    uint16_t h =
        ((uint16_t)packet[6] << 8) |
        packet[7];


    // =================================================
    // FLUSH PACKET
    // =================================================

    if (w == FLUSH_W && h == FLUSH_H)
    {
        Serial.write('K');
        return;
    }


    // =================================================
    // VALIDATION
    // =================================================

    if (w == 0 || h == 0)
        return;

    if (w > TILE_MAX || h > TILE_MAX)
        return;

    if (x >= TFT_W || y >= TFT_H)
        return;

    if ((uint32_t)x + w > TFT_W)
        return;

    if ((uint32_t)y + h > TFT_H)
        return;


    // =================================================
    // PIXEL DATA
    // =================================================

    uint16_t totalPixels = w * h;

    uint16_t totalBytes = totalPixels * 2;


    uint8_t *raw =
        reinterpret_cast<uint8_t *>(tileBuf);


    if (!readExact(raw, totalBytes))
        return;


    // =================================================
    // TFT WINDOW
    // =================================================

    tft.setAddrWindow(
        x,
        y,
        w,
        h
    );


    // =================================================
    // TFT WRITE
    // =================================================

    tft.pushColors(
        tileBuf,
        totalPixels,
        false
    );


    // =================================================
    // NO ACK HERE
    //
    // Python이 16개 타일을 보낸 후
    // FLUSH 패킷을 보내면 그때 ACK
    // =================================================

    yield();
}