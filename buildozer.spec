[app]

# (str) Title of your application
title = Mi Calculadora de Ingenieria

# (str) Package name
package.name = calculadoraingenieria

# (str) Package domain (needed for android packaging)
package.domain = org.ingenieria

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Source directory where the application lives
source.dir = .

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,sdl2,sdl2_image,sdl2_ttf,sdl2_mixer

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
