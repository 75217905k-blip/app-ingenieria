[app]

# (str) Title of your application
title = Calculadora de Ingenieria

# (str) Package name
package.name = calculadoraingenieria

# (str) Package domain (needed for android packaging)
package.domain = org.ingenieria

# (list) Source files to include (let it empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to include (let it empty to include all the files)
source.dir = .

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,kivymd,pillow,certifi

# (list) Permissions
android.permissions = INTERNET

# (str) Supported orientations
orientation = portrait

# (list) List of service to declare
#services = 

[buildozer]

# (int) Log level (0 = error, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
