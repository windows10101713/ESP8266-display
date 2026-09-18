# ESP8266-display

**PC 화면을 ESP8266 + TFT 디스플레이로 출력하는 프로젝트**

> Python이 화면을 캡처하고, UART로 ESP8266에 전송하면
> ESP8266이 받은 화면 데이터를 TFT에 출력합니다.

---

## 🇰🇷 한국어

### 개요

`ESP8266-display`는 **ESP8266을 화면 출력 장치로 사용하는 프로젝트**입니다.

컴퓨터에서 Python 프로그램이 화면을 캡처하고 필요한 부분만 찾아서 UART로 전송합니다.
ESP8266은 UART 데이터를 받아 TFT 디스플레이에 출력합니다.

```text
┌──────────────┐
│   Computer   │
│              │
│ Python       │
│ Screen       │
│ Capture      │
└──────┬───────┘
       │ UART
       ▼
┌──────────────┐
│   ESP8266    │
│              │
│ UART Receive │
│ Data Decode  │
└──────┬───────┘
       │ SPI
       ▼
┌──────────────┐
│ TFT Display  │
│   480×320    │
└──────────────┘
```

### 주요 기능

* Python 기반 화면 캡처
* 화면을 `480×320`으로 변환
* RGB565 형식 사용
* 변경된 영역만 전송
* `16×16` 타일 기반 화면 업데이트
* UART 통신
* ESP8266에서 TFT 출력
* 데이터 전송 후 ACK를 이용한 동기화

### 하드웨어

현재 프로젝트의 기본 구성:

* ESP8266 NodeMCU
* TFT LCD
* ILI9488
* SPI 연결
* USB-UART
* PC

### 소프트웨어

Python:

* Python 3
* `mss`
* `Pillow`
* `pyserial`

ESP8266:

* Arduino
* ESP8266 Arduino Core
* TFT_eSPI

### 통신

기본 UART 속도:

```text
1,500,000 baud
```

화면 데이터는 RGB565를 사용합니다.

각 타일은 다음과 같은 구조로 전송됩니다.

```text
HEADER
X
Y
WIDTH
HEIGHT
RGB565 DATA
```

ESP8266이 한 번에 여러 타일을 받은 뒤 `K`를 반환하여 전송 완료를 알립니다.

### 왜 전체 화면을 보내지 않는가?

480×320 화면을 RGB565로 보내면 한 프레임에:

```text
480 × 320 × 2
= 307,200 bytes
```

가 필요합니다.

따라서 화면 전체를 계속 보내는 대신 **변경된 타일만 전송**합니다.

```text
화면
┌──┬──┬──┬──┬──┐
│  │██│  │  │  │
├──┼──┼──┼──┼──┤
│  │██│  │██│  │
├──┼──┼──┼──┼──┤
│  │  │  │██│  │
└──┴──┴──┴──┴──┘

██ = 변경된 영역만 전송
```

### 실행

PC에서:

```bash
pip install mss pillow pyserial
```

그 다음:

```bash
python display.py
```

ESP8266에:

```text
uart-display.ino
```

를 업로드합니다.

### 프로젝트 상태

> Experimental

아직 완성된 상용 제품이 아닙니다.

목표는 단순합니다.

**"ESP8266을 작은 외부 디스플레이로 만들어 보자."**

---

# 🇺🇸 English

## Overview

`ESP8266-display` is a project that uses an **ESP8266 as a display device**.

A Python program captures the computer screen, detects the changed areas, and sends the data through UART.

The ESP8266 receives the UART data and renders it on a TFT display.

```text
Computer
   │
   │ Python
   │ Screen Capture
   ▼
 UART
   │
   ▼
ESP8266
   │
   │ SPI
   ▼
TFT Display
480×320
```

## Features

* Python screen capture
* Resize to `480×320`
* RGB565 color format
* Dirty-region detection
* `16×16` tile-based updates
* UART communication
* ESP8266 TFT rendering
* ACK-based synchronization

## Hardware

Basic hardware:

* ESP8266 NodeMCU
* TFT LCD
* ILI9488
* SPI connection
* USB-UART
* Computer

## Software

Python:

* Python 3
* `mss`
* `Pillow`
* `pyserial`

ESP8266:

* Arduino
* ESP8266 Arduino Core
* TFT_eSPI

## Communication

Default UART speed:

```text
1,500,000 baud
```

Pixel data uses RGB565.

A tile packet contains:

```text
HEADER
X
Y
WIDTH
HEIGHT
RGB565 DATA
```

After receiving a batch of tiles, the ESP8266 sends `K` as an acknowledgement.

## Why not send the entire screen?

A `480×320` RGB565 frame requires:

```text
480 × 320 × 2
= 307,200 bytes
```

Instead of continuously sending the entire frame, this project sends **only changed tiles**.

This reduces unnecessary data transmission.

## Installation

Install the Python dependencies:

```bash
pip install mss pillow pyserial
```

Run:

```bash
python display.py
```

Upload:

```text
uart-display.ino
```

to the ESP8266.

## Project Status

> Experimental

This is not a finished commercial product.

The idea is simple:

**"Turn an ESP8266 into a small external display."**

---

# 🇩🇪 Deutsch

## Übersicht

`ESP8266-display` ist ein Projekt, bei dem ein **ESP8266 als Anzeigegerät** verwendet wird.

Ein Python-Programm nimmt den Bildschirm des Computers auf, erkennt die geänderten Bereiche und sendet die Daten über UART.

Der ESP8266 empfängt die UART-Daten und zeigt sie auf einem TFT-Display an.

```text
Computer
   │
   │ Python
   │ Bildschirmaufnahme
   ▼
 UART
   │
   ▼
ESP8266
   │
   │ SPI
   ▼
TFT-Display
480×320
```

## Funktionen

* Bildschirmaufnahme mit Python
* Skalierung auf `480×320`
* RGB565-Farbformat
* Erkennung geänderter Bereiche
* Aktualisierung mit `16×16`-Kacheln
* UART-Kommunikation
* TFT-Ausgabe mit ESP8266
* Synchronisierung über ACK

## Hardware

Grundaufbau:

* ESP8266 NodeMCU
* TFT-LCD
* ILI9488
* SPI-Verbindung
* USB-UART
* Computer

## Software

Python:

* Python 3
* `mss`
* `Pillow`
* `pyserial`

ESP8266:

* Arduino
* ESP8266 Arduino Core
* TFT_eSPI

## Kommunikation

Standardmäßige UART-Geschwindigkeit:

```text
1.500.000 Baud
```

Die Pixeldaten verwenden RGB565.

Ein Kachelpaket enthält:

```text
HEADER
X
Y
WIDTH
HEIGHT
RGB565 DATA
```

Nachdem der ESP8266 einen Kachel-Block empfangen hat, sendet er `K` als Bestätigung zurück.

## Warum wird nicht der gesamte Bildschirm übertragen?

Ein RGB565-Bild mit `480×320` Pixeln benötigt:

```text
480 × 320 × 2
= 307.200 Bytes
```

Deshalb wird nicht ständig der gesamte Bildschirm übertragen.

Stattdessen werden **nur geänderte Kacheln** gesendet.

Dadurch werden unnötige Datenübertragungen reduziert.

## Installation

Python-Abhängigkeiten installieren:

```bash
pip install mss pillow pyserial
```

Starten:

```bash
python display.py
```

Auf den ESP8266 hochladen:

```text
uart-display.ino
```

## Projektstatus

> Experimental

Dieses Projekt ist noch kein fertiges kommerzielles Produkt.

Die Idee ist einfach:

**„Machen wir aus einem ESP8266 ein kleines externes Display.“**

---

# 🇯🇵 日本語

## 概要

`ESP8266-display` は、**ESP8266をディスプレイ装置として使用するプロジェクト**です。

Pythonプログラムがコンピューターの画面をキャプチャし、変更された部分を検出してUART経由でESP8266へ送信します。

ESP8266はUARTデータを受信し、TFTディスプレイに表示します。

```text
コンピューター
     │
     │ Python
     │ 画面キャプチャ
     ▼
   UART
     │
     ▼
  ESP8266
     │
     │ SPI
     ▼
TFTディスプレイ
   480×320
```

## 主な機能

* Pythonによる画面キャプチャ
* `480×320`へのリサイズ
* RGB565カラーフォーマット
* 変更された領域の検出
* `16×16`タイル方式による更新
* UART通信
* ESP8266によるTFT表示
* ACKによる同期

## ハードウェア

基本構成:

* ESP8266 NodeMCU
* TFT LCD
* ILI9488
* SPI接続
* USB-UART
* コンピューター

## ソフトウェア

Python:

* Python 3
* `mss`
* `Pillow`
* `pyserial`

ESP8266:

* Arduino
* ESP8266 Arduino Core
* TFT_eSPI

## 通信

UARTの標準速度:

```text
1,500,000 baud
```

画像データにはRGB565を使用します。

1つのタイルパケットは次の形式です。

```text
HEADER
X
Y
WIDTH
HEIGHT
RGB565 DATA
```

ESP8266が複数のタイルを受信すると、`K`をACKとして返します。

## なぜ画面全体を送信しないのか？

`480×320`のRGB565画像では、

```text
480 × 320 × 2
= 307,200 bytes
```

が必要になります。

そのため、画面全体を毎回送信するのではなく、**変更されたタイルだけを送信**します。

これにより、不要なデータ転送を減らします。

## インストール

Pythonの必要なライブラリをインストール:

```bash
pip install mss pillow pyserial
```

実行:

```bash
python display.py
```

ESP8266には:

```text
uart-display.ino
```

をアップロードしてください。

## プロジェクトの状態

> Experimental

まだ完成した製品ではありません。

目的はシンプルです。

**「ESP8266を小さな外部ディスプレイにしてみよう。」**
