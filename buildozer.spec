[app]
title = UmBala
package.name = umbala
package.domain = kz.umbala

source.dir = .
source.include_exts = py,png,jpg,kv,json,atlas,ttf
version = 0.1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1

# Сборка (на Linux/WSL, не на Windows напрямую):
#   pip install buildozer
#   buildozer -v android debug
# Готовый APK появится в bin/
