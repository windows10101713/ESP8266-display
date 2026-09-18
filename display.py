# ============================================================
# ARDUDOWS UNIVERSAL DISPLAY
# AUTO DEVICE / OS / SERIAL DETECTION
#
# 기존 화면 전송 로직은 그대로 유지
# 초반 장치 검사 + 포트 선택 + OS 검사만 자동화
# ============================================================

import sys
import time
import struct
import platform

import serial
import serial.tools.list_ports

import mss
import numpy as np

from PIL import Image


# ============================================================
# AUTO SYSTEM DETECTION
# ============================================================

OS_NAME = platform.system()

if OS_NAME == "Windows":
    OS_TYPE = "WINDOWS"

elif OS_NAME == "Linux":
    OS_TYPE = "LINUX"

elif OS_NAME == "Darwin":
    OS_TYPE = "MACOS"

else:
    OS_TYPE = "UNKNOWN"


# ============================================================
# CONFIG
# ============================================================

# 자동 검색 결과가 들어갈 곳
PORT = None

# 화면 해상도도 자동 검색
SRC_W = None
SRC_H = None

# 2M은 현재 불안정하므로 1.5M 사용
BAUD = 1500000

TFT_W = 480
TFT_H = 320

TILE = 16

GRID_W = TFT_W // TILE
GRID_H = TFT_H // TILE

HEADER = 0xAA

# 몇 개의 타일을 모아서 한 번에 보낼지
BATCH_TILES = 16

# packet:
# HEADER + X + Y + W + H
PACK = struct.Struct(">BHHHH")


# ============================================================
# DEVICE SCAN
# ============================================================

def scan_devices():

    print("========================================")
    print(" DEVICE AUTO DETECTION")
    print("========================================")

    print()
    print("OS detected:")
    print(" ", OS_NAME)
    print()

    ports = list(
        serial.tools.list_ports.comports()
    )

    if not ports:

        print("No serial devices detected.")
        print()
        print("Connect ESP8266 and restart.")
        sys.exit(1)


    print("Serial devices detected:")
    print()


    scored = []


    for device in ports:

        text = " ".join([
            str(device.device),
            str(device.description),
            str(device.manufacturer),
            str(device.product),
            str(device.hwid),
        ]).lower()


        score = 0


        # ----------------------------------------------------
        # ESP
        # ----------------------------------------------------

        if "esp8266" in text:
            score += 1000

        if "esp32" in text:
            score += 1000


        # ----------------------------------------------------
        # USB UART
        # ----------------------------------------------------

        if "ch340" in text:
            score += 900

        if "ch341" in text:
            score += 900

        if "cp210" in text:
            score += 800

        if "silicon labs" in text:
            score += 700


        # ----------------------------------------------------
        # Generic USB serial
        # ----------------------------------------------------

        if "usb serial" in text:
            score += 600

        if "usb-enhanced" in text:
            score += 600

        if "uart" in text:
            score += 500

        if "serial" in text:
            score += 100


        scored.append(
            (
                score,
                device
            )
        )


    # 높은 점수 우선
    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )


    for score, device in scored:

        print(
            f"  {device.device:<8} "
            f"score={score:<4} "
            f"{device.description}"
        )


    print()


    # --------------------------------------------------------
    # 자동 선택
    # --------------------------------------------------------

    selected_score, selected = scored[0]


    global PORT

    PORT = selected.device


    print(
        "Selected serial device:",
        PORT
    )

    print()


# ============================================================
# SCREEN AUTO DETECTION
# ============================================================

def detect_screen():

    global SRC_W
    global SRC_H

    print("Detecting display...")


    with mss.MSS() as detector:

        monitors = detector.monitors


        if len(monitors) < 2:

            print(
                "No primary monitor detected."
            )

            sys.exit(1)


        # 기존 코드가 사용하던 primary monitor
        monitor = monitors[1]


        SRC_W = int(
            monitor["width"]
        )

        SRC_H = int(
            monitor["height"]
        )


    print(
        "Primary display:",
        f"{SRC_W} x {SRC_H}"
    )

    print()


# ============================================================
# DEVICE TEST
# ============================================================

def test_serial_device():

    print("Testing serial device...")
    print(
        f"Port : {PORT}"
    )
    print(
        f"Baud : {BAUD}"
    )
    print()


    try:

        test = serial.Serial(

            PORT,
            BAUD,

            timeout=0.2,
            write_timeout=3,

            dsrdtr=False,
            rtscts=False
        )


        try:

            test.dtr = False
            test.rts = False

        except Exception:
            pass


        # ESP boot 시간
        time.sleep(2)


        # 부팅 과정에서 남아 있는 데이터 제거
        test.reset_input_buffer()
        test.reset_output_buffer()


        test.close()


        print(
            "Serial device test: OK"
        )

        print()


    except Exception as e:

        print()
        print(
            "Serial device test FAILED:"
        )

        print(e)

        print()

        print(
            "The selected port could not be opened."
        )

        print()

        sys.exit(1)


# ============================================================
# INITIAL AUTO SETUP
# ============================================================

print()
print("========================================")
print(" ARDUDOWS UNIVERSAL DISPLAY CLIENT")
print("========================================")
print(
    "OS     :",
    OS_NAME
)
print(
    "Python :",
    platform.python_version()
)
print(
    "Baud   :",
    BAUD
)
print(
    "Output :",
    TFT_W,
    "x",
    TFT_H
)
print(
    "Tile   :",
    TILE,
    "x",
    TILE
)
print(
    "Batch  :",
    BATCH_TILES
)
print("========================================")
print()


# 자동 OS 검사
if OS_TYPE == "UNKNOWN":

    print(
        "Unsupported operating system:"
    )

    print(OS_NAME)

    sys.exit(1)


# 장치 검색
scan_devices()


# 화면 검색
detect_screen()


# 포트 열기 테스트
test_serial_device()


# ============================================================
# WINDOWS API
# ============================================================

# Windows일 때만 로드
if OS_TYPE == "WINDOWS":

    import ctypes
    from ctypes import wintypes


    user32 = ctypes.WinDLL(
        "user32",
        use_last_error=True
    )


    gdi32 = ctypes.WinDLL(
        "gdi32",
        use_last_error=True
    )


    # ========================================================
    # CURSORINFO
    # ========================================================

    class CURSORINFO(ctypes.Structure):

        _fields_ = [

            ("cbSize", wintypes.DWORD),

            ("flags", wintypes.DWORD),

            ("hCursor", wintypes.HANDLE),

            ("ptScreenPos", wintypes.POINT),

        ]


    # ========================================================
    # ICONINFO
    # ========================================================

    class ICONINFO(ctypes.Structure):

        _fields_ = [

            ("fIcon", wintypes.BOOL),

            ("xHotspot", wintypes.DWORD),

            ("yHotspot", wintypes.DWORD),

            ("hbmMask", wintypes.HBITMAP),

            ("hbmColor", wintypes.HBITMAP),

        ]


    # ========================================================
    # BITMAP
    # ========================================================

    class BITMAP(ctypes.Structure):

        _fields_ = [

            ("bmType", wintypes.LONG),

            ("bmWidth", wintypes.LONG),

            ("bmHeight", wintypes.LONG),

            ("bmWidthBytes", wintypes.LONG),

            ("bmPlanes", wintypes.WORD),

            ("bmBitsPixel", wintypes.WORD),

            ("bmBits", wintypes.LPVOID),

        ]


    # ========================================================
    # BITMAPINFOHEADER
    # ========================================================

    class BITMAPINFOHEADER(ctypes.Structure):

        _fields_ = [

            ("biSize", wintypes.DWORD),

            ("biWidth", wintypes.LONG),

            ("biHeight", wintypes.LONG),

            ("biPlanes", wintypes.WORD),

            ("biBitCount", wintypes.WORD),

            ("biCompression", wintypes.DWORD),

            ("biSizeImage", wintypes.DWORD),

            ("biXPelsPerMeter", wintypes.LONG),

            ("biYPelsPerMeter", wintypes.LONG),

            ("biClrUsed", wintypes.DWORD),

            ("biClrImportant", wintypes.DWORD),

        ]


    class BITMAPINFO(ctypes.Structure):

        _fields_ = [

            (
                "bmiHeader",
                BITMAPINFOHEADER
            ),

            (
                "bmiColors",
                wintypes.DWORD * 3
            ),

        ]


    # ========================================================
    # CONSTANTS
    # ========================================================

    BI_RGB = 0

    DIB_RGB_COLORS = 0

    CURSOR_SHOWING = 0x00000001

    DI_NORMAL = 0x0003


    # ========================================================
    # API PROTOTYPES
    # ========================================================

    user32.GetCursorInfo.argtypes = [

        ctypes.POINTER(
            CURSORINFO
        )

    ]

    user32.GetCursorInfo.restype = (
        wintypes.BOOL
    )


    user32.GetIconInfo.argtypes = [

        wintypes.HICON,

        ctypes.POINTER(
            ICONINFO
        )

    ]

    user32.GetIconInfo.restype = (
        wintypes.BOOL
    )


    user32.GetDC.argtypes = [

        wintypes.HWND

    ]

    user32.GetDC.restype = (
        wintypes.HDC
    )


    user32.ReleaseDC.argtypes = [

        wintypes.HWND,

        wintypes.HDC

    ]

    user32.ReleaseDC.restype = (
        ctypes.c_int
    )


    user32.DrawIconEx.argtypes = [

        wintypes.HDC,

        ctypes.c_int,

        ctypes.c_int,

        wintypes.HICON,

        ctypes.c_int,

        ctypes.c_int,

        ctypes.c_uint,

        wintypes.HBRUSH,

        ctypes.c_uint

    ]

    user32.DrawIconEx.restype = (
        wintypes.BOOL
    )


    gdi32.GetObjectW.argtypes = [

        wintypes.HGDIOBJ,

        ctypes.c_int,

        wintypes.LPVOID

    ]

    gdi32.GetObjectW.restype = (
        ctypes.c_int
    )


    gdi32.CreateCompatibleDC.argtypes = [

        wintypes.HDC

    ]

    gdi32.CreateCompatibleDC.restype = (
        wintypes.HDC
    )


    gdi32.DeleteDC.argtypes = [

        wintypes.HDC

    ]

    gdi32.DeleteDC.restype = (
        wintypes.BOOL
    )


    gdi32.CreateDIBSection.argtypes = [

        wintypes.HDC,

        ctypes.POINTER(
            BITMAPINFO
        ),

        wintypes.UINT,

        ctypes.POINTER(
            wintypes.LPVOID
        ),

        wintypes.HANDLE,

        wintypes.DWORD

    ]

    gdi32.CreateDIBSection.restype = (
        wintypes.HBITMAP
    )


    gdi32.SelectObject.argtypes = [

        wintypes.HDC,

        wintypes.HGDIOBJ

    ]

    gdi32.SelectObject.restype = (
        wintypes.HGDIOBJ
    )


    gdi32.DeleteObject.argtypes = [

        wintypes.HGDIOBJ

    ]

    gdi32.DeleteObject.restype = (
        wintypes.BOOL
    )


# ============================================================
# CURSOR CACHE
# ============================================================

cached_cursor_handle = None

cached_cursor_image = None

cached_hotspot_x = 0
cached_hotspot_y = 0


# ============================================================
# CAPTURE CURSOR IMAGE
# ============================================================

def capture_cursor_image(hcursor):

    if OS_TYPE != "WINDOWS":

        return None


    ii = ICONINFO()


    if not user32.GetIconInfo(
        hcursor,
        ctypes.byref(ii)
    ):

        return None


    try:

        bmp = BITMAP()


        if ii.hbmColor:

            if not gdi32.GetObjectW(

                ii.hbmColor,

                ctypes.sizeof(bmp),

                ctypes.byref(bmp)

            ):

                return None


            width = bmp.bmWidth

            height = bmp.bmHeight


        else:

            if not gdi32.GetObjectW(

                ii.hbmMask,

                ctypes.sizeof(bmp),

                ctypes.byref(bmp)

            ):

                return None


            width = bmp.bmWidth

            height = bmp.bmHeight // 2


        if width <= 0 or height <= 0:

            return None


        width = min(
            width,
            128
        )

        height = min(
            height,
            128
        )


        screen_dc = user32.GetDC(
            None
        )


        if not screen_dc:

            return None


        mem_dc = gdi32.CreateCompatibleDC(
            screen_dc
        )


        if not mem_dc:

            user32.ReleaseDC(
                None,
                screen_dc
            )

            return None


        dib = None

        old_obj = None


        try:

            bmi = BITMAPINFO()


            bmi.bmiHeader.biSize = (
                ctypes.sizeof(
                    BITMAPINFOHEADER
                )
            )

            bmi.bmiHeader.biWidth = (
                width
            )

            bmi.bmiHeader.biHeight = (
                -height
            )

            bmi.bmiHeader.biPlanes = 1

            bmi.bmiHeader.biBitCount = 32

            bmi.bmiHeader.biCompression = (
                BI_RGB
            )


            bits = wintypes.LPVOID()


            dib = gdi32.CreateDIBSection(

                mem_dc,

                ctypes.byref(bmi),

                DIB_RGB_COLORS,

                ctypes.byref(bits),

                None,

                0

            )


            if not dib:

                return None


            old_obj = gdi32.SelectObject(

                mem_dc,

                dib

            )


            ctypes.memset(

                bits,

                0,

                width * height * 4

            )


            user32.DrawIconEx(

                mem_dc,

                0,

                0,

                hcursor,

                width,

                height,

                0,

                None,

                DI_NORMAL

            )


            raw = ctypes.string_at(

                bits,

                width * height * 4

            )


            arr = np.frombuffer(

                raw,

                dtype=np.uint8

            ).reshape(

                height,

                width,

                4

            )


            rgba = arr[
                :,
                :,
                [2, 1, 0, 3]
            ].copy()


            cursor_img = Image.fromarray(

                rgba,

                "RGBA"

            )


            return (

                cursor_img,

                int(ii.xHotspot),

                int(ii.yHotspot)

            )


        finally:

            if old_obj:

                gdi32.SelectObject(

                    mem_dc,

                    old_obj

                )


            if dib:

                gdi32.DeleteObject(
                    dib
                )


            gdi32.DeleteDC(
                mem_dc
            )


            user32.ReleaseDC(

                None,

                screen_dc

            )


    finally:

        if ii.hbmMask:

            gdi32.DeleteObject(
                ii.hbmMask
            )


        if ii.hbmColor:

            gdi32.DeleteObject(
                ii.hbmColor
            )


# ============================================================
# GET CURSOR
# ============================================================

def get_cursor_fast():

    global cached_cursor_handle

    global cached_cursor_image

    global cached_hotspot_x

    global cached_hotspot_y


    if OS_TYPE != "WINDOWS":

        return None


    ci = CURSORINFO()


    ci.cbSize = ctypes.sizeof(
        CURSORINFO
    )


    if not user32.GetCursorInfo(

        ctypes.byref(ci)

    ):

        return None


    if not (
        ci.flags &
        CURSOR_SHOWING
    ):

        return None


    hcursor = ci.hCursor


    if hcursor != cached_cursor_handle:

        result = capture_cursor_image(
            hcursor
        )


        if result is None:

            cached_cursor_handle = None

            cached_cursor_image = None

            return None


        (
            cached_cursor_image,
            cached_hotspot_x,
            cached_hotspot_y
        ) = result


        cached_cursor_handle = hcursor


    return (

        cached_cursor_image,

        cached_hotspot_x,

        cached_hotspot_y,

        int(ci.ptScreenPos.x),

        int(ci.ptScreenPos.y)

    )


# ============================================================
# UART
# ============================================================

ser = serial.Serial(

    PORT,

    BAUD,

    timeout=1,

    write_timeout=3,

    dsrdtr=False,

    rtscts=False

)


try:

    ser.dtr = False
    ser.rts = False

except Exception:

    pass


time.sleep(2)


print()
print("========================================")
print(" ESP8266 ULTRA FAST UART DISPLAY")
print("========================================")
print("OS     :", OS_NAME)
print("UART   :", PORT)
print("BAUD   :", BAUD)
print("Source :", SRC_W, "x", SRC_H)
print("Output :", TFT_W, "x", TFT_H)
print("Tile   :", TILE, "x", TILE)
print("Batch  :", BATCH_TILES, "tiles")
print(
    "Cursor :",
    "REAL WINDOWS CURSOR + CACHE"
    if OS_TYPE == "WINDOWS"
    else "OS CURSOR API DISABLED"
)
print("========================================")
print()


# ============================================================
# WAIT ESP READY
# ============================================================

print("Waiting for ESP8266...")


while True:

    if ser.read(1) == b"R":

        break


ser.reset_input_buffer()


print("READY")
print()


# ============================================================
# MSS
# ============================================================

sct = mss.MSS()


# ============================================================
# PREVIOUS FRAME
# ============================================================

prev = np.zeros(

    (TFT_H, TFT_W),

    dtype=np.uint16

)


# ============================================================
# PREVIOUS CURSOR
# ============================================================

prev_cursor_box = None


# ============================================================
# DIRTY BOX
# ============================================================

def mark_box(diff, box):

    if box is None:

        return


    x1, y1, x2, y2 = box


    x1 = max(
        0,
        min(
            TFT_W,
            int(x1)
        )
    )


    y1 = max(
        0,
        min(
            TFT_H,
            int(y1)
        )
    )


    x2 = max(
        0,
        min(
            TFT_W,
            int(x2)
        )
    )


    y2 = max(
        0,
        min(
            TFT_H,
            int(y2)
        )
    )


    if x2 > x1 and y2 > y1:

        diff[
            y1:y2,
            x1:x2
        ] = True


# ============================================================
# SEND BATCH
# ============================================================

def send_batch(packets):

    if not packets:

        return


    batch = bytearray()


    for packet in packets:

        batch.extend(packet)


    ser.write(batch)


    # FLUSH
    ser.write(

        PACK.pack(

            HEADER,

            0,

            0,

            0,

            0

        )

    )


    ack = ser.read(1)


    if ack != b"K":

        raise RuntimeError(

            "ESP8266 ACK timeout / "
            "protocol desync"

        )


# ============================================================
# MAIN
# ============================================================

try:

    frame_count = 0

    total_tiles = 0

    start_time = (
        time.perf_counter()
    )


    while True:

        frame_start = (
            time.perf_counter()
        )


        # ====================================================
        # SCREEN CAPTURE
        # ====================================================

        shot = sct.grab({

            "left": 0,

            "top": 0,

            "width": SRC_W,

            "height": SRC_H

        })


        img = Image.frombytes(

            "RGB",

            shot.size,

            shot.rgb

        )


        # ====================================================
        # RESIZE
        # ====================================================

        img = img.resize(

            (TFT_W, TFT_H),

            Image.Resampling.BILINEAR

        )


        # ====================================================
        # CURSOR
        # ====================================================

        cursor = get_cursor_fast()

        current_cursor_box = None


        if cursor is not None:

            (
                cursor_img,
                hotspot_x,
                hotspot_y,
                mouse_x,
                mouse_y
            ) = cursor


            screen_cursor_x = (

                mouse_x
                * TFT_W
                / SRC_W

            )


            screen_cursor_y = (

                mouse_y
                * TFT_H
                / SRC_H

            )


            cursor_x = int(

                screen_cursor_x
                -
                hotspot_x
                * TFT_W
                / SRC_W

            )


            cursor_y = int(

                screen_cursor_y
                -
                hotspot_y
                * TFT_H
                / SRC_H

            )


            cursor_w = max(

                1,

                int(

                    cursor_img.width
                    * TFT_W
                    / SRC_W

                )

            )


            cursor_h = max(

                1,

                int(

                    cursor_img.height
                    * TFT_H
                    / SRC_H

                )

            )


            if (

                cursor_img.width
                != cursor_w

                or

                cursor_img.height
                != cursor_h

            ):

                cursor_img_small = (
                    cursor_img.resize(

                        (
                            cursor_w,
                            cursor_h
                        ),

                        Image.Resampling.NEAREST

                    )
                )

            else:

                cursor_img_small = (
                    cursor_img
                )


            img = img.convert(
                "RGBA"
            )


            img.alpha_composite(

                cursor_img_small,

                (
                    cursor_x,
                    cursor_y
                )

            )


            img = img.convert(
                "RGB"
            )


            current_cursor_box = (

                cursor_x,

                cursor_y,

                cursor_x + cursor_w,

                cursor_y + cursor_h

            )


        # ====================================================
        # RGB565
        # ====================================================

        rgb = np.asarray(

            img,

            dtype=np.uint16

        )


        rgb565 = (

            ((rgb[:, :, 0] >> 3) << 11)

            |

            ((rgb[:, :, 1] >> 2) << 5)

            |

            (rgb[:, :, 2] >> 3)

        )


        # ====================================================
        # DIFFERENCE
        # ====================================================

        diff = (
            rgb565 != prev
        )


        mark_box(

            diff,

            prev_cursor_box

        )


        mark_box(

            diff,

            current_cursor_box

        )


        # ====================================================
        # TILE DIFF
        # ====================================================

        tile_diff = diff.reshape(

            GRID_H,

            TILE,

            GRID_W,

            TILE

        ).any(

            axis=(1, 3)

        )


        active_tiles = np.argwhere(

            tile_diff

        )


        tile_count = len(
            active_tiles
        )


        # ====================================================
        # SEND
        # ====================================================

        batch_packets = []

        batch_count = 0


        for by, bx in active_tiles:

            x = int(bx) * TILE

            y = int(by) * TILE


            tile = rgb565[

                y:y + TILE,

                x:x + TILE

            ]


            h, w = tile.shape


            pixel_bytes = (

                tile.byteswap()

                .tobytes()

            )


            packet = (

                PACK.pack(

                    HEADER,

                    x,

                    y,

                    w,

                    h

                )

                +

                pixel_bytes

            )


            batch_packets.append(
                packet
            )


            batch_count += 1


            if batch_count >= BATCH_TILES:

                send_batch(

                    batch_packets

                )


                batch_packets.clear()

                batch_count = 0


        # ====================================================
        # LAST BATCH
        # ====================================================

        if batch_packets:

            send_batch(

                batch_packets

            )


        # ====================================================
        # SAVE FRAME
        # ====================================================

        prev[:] = rgb565

        prev_cursor_box = (
            current_cursor_box
        )


        # ====================================================
        # STATS
        # ====================================================

        frame_count += 1

        total_tiles += tile_count


        elapsed = (

            time.perf_counter()

            - start_time

        )


        frame_time = (

            time.perf_counter()

            - frame_start

        )


        fps = (

            1.0 / frame_time

            if frame_time > 0

            else 0

        )


        if frame_count % 10 == 0:

            avg_tiles = (

                total_tiles
                /
                frame_count

            )


            print(

                f"\r"

                f"Frame: "
                f"{frame_count:6d} | "

                f"Tiles: "
                f"{tile_count:4d} | "

                f"Avg: "
                f"{avg_tiles:6.1f} | "

                f"{fps:6.2f} FPS",

                end="",

                flush=True

            )


except KeyboardInterrupt:

    print(
        "\n\nMirror stopped."
    )


except Exception as e:

    print(
        "\n\nERROR:",
        e
    )


finally:

    ser.close()

    sct.close()
