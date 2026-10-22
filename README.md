# LionCut Studio 🦁

Windows uchun Python + Tkinter + FFmpeg asosida yaratilayotgan video montaj dasturi.

## 0.1 funksiyalari
- MP4, MOV, MKV, AVI, WEBM import
- Kliplarni tartiblash va o'chirish
- Boshlanish va tugash soniyalarini belgilab kesish
- Bir kadrni ko'rish
- .lioncut loyiha formatida saqlash/ochish
- Videolarni 720p/30 FPS/H.264 MP4 qilib birlashtirish

**Hozircha cheklov:** eksport video-only, ovoz saqlanmaydi. Bu Adobe Premiere Pro o'rnini bosadigan to'liq muharrir emas; rivojlanishdagi dastlabki versiya.

## Windows'da ishga tushirish
1. Python 3.10+ o'rnating (PATH qo'shilgan bo'lsin).
2. FFmpeg va FFprobe o'rnating: terminalda `ffmpeg -version`, `ffprobe -version` ishlashi kerak.
3. `start.bat` faylini ishga tushiring yoki terminalda:

```powershell
py -3 -m pip install -r requirements.txt
py -3 main.py
```

## GitHub orqali yuklab olish
Repository sahifasida **Code > Download ZIP** yoki `git clone https://github.com/Amanbayevv-cloud/LionCut-Studio.git`.

## Reja
Keyingi versiyalarda audio, timeline, playback, effektlar va eksport sozlamalari qo'shiladi.
