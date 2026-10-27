# (list) Application requirements
# Cambiamos temporalmente quitando pillow y certifi si causan conflicto en p4a, o dejamos los básicos estables
requirements = python3,kivy,kivymd

# (list) Supported architectures
# Forzamos solo arm64-v8a para evitar conflictos de compilación cruzada en el servidor de GitHub
android.archs = arm64-v8a

# (int) Target Android API
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use (fijo en una versión súper estable para python-for-android)
android.ndk = 25b

# (bool) Indicate if you want to accept Android SDK licenses
android.accept_sdk_license = True
