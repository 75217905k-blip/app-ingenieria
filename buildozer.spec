[app]

# (str) Title of your application
title = Calculadora de Ingenieria

# (str) Package name
package.name = calculadoraingenieria

# (str) Package domain (needed for android packaging)
package.domain = org.ingenieria

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to include
source.dir = .

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,kivymd,pillow,certifi

# (list) Supported architectures
android.archs = arm64-v8a

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (str) Supported orientations
orientation = portrait

# (int) Target Android API
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Indicate if you want to accept Android SDK licenses
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
