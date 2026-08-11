[app]

# (str) Title of your application
title = Forex Signal Bot

# (str) Package name
package.name = forexsignalbot

# (str) Package domain
package.domain = org.forexsignal

# (str) Source code directory
source.dir = .

# (str) Application version
version = 1.0

# (str) Supported source file extensions
source.include_exts = py,png,jpg,jpeg,kv,json

# (str) Application requirements
requirements = python3,kivy,requests

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0


[app:android]

# (list) Android permissions
android.permissions = INTERNET

# (int) Android API level
android.api = 34

# (int) Minimum Android API
android.minapi = 23

# (str) Android architecture
android.archs = arm64-v8a

# (bool) Accept Android SDK license
android.accept_sdk_license = True


[buildozer]

# (int) Log level
log_level = 2

# (bool) Warn when running buildozer as root
warn_on_root = 1
