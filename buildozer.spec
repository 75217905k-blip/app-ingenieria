[app]

title = Calculadora de Ingenieria
package.name = calculadoraingenieria
package.domain = org.ingenieria

source.include_exts = py,png,jpg,kv,atlas
source.dir = .

version = 0.1

# Requerimientos limpios solo con kivy
requirements = python3,kivy

android.archs = arm64-v8a
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

orientation = portrait
android.api = 31
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
