[app]

title = Forex Signal Bot
package.name = forexsignalbot
package.domain = org.forexsignal

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json

version = 1.0

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 35
android.minapi = 21

android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
