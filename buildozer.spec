[app]

# (str) Title of your application
title = Mi Calculadora de Ingenieria

# (str) Package name
package.name = calculadoraingenieria

# (str) Package domain (needed for android packaging)
package.domain = org.ingenieria

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1