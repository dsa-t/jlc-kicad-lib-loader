# JLCPCB/LCSC Library Loader

This KiCad plugin allows you to search and download symbols/footprints with 3D models to a local .elibz library that can be read by KiCad.

![image](https://github.com/user-attachments/assets/37e16749-94ea-46e8-88c9-e85164eaf495)

# System support

- **KiCad**: version 8.0.7 or newer.
- **Windows**: version 10 or newer with normal KiCad installation.
- **Ubuntu**: install KiCad from PPA. To make the preview work, install `python3-wxgtk-webview4.0`.
- **Flatpak**: works but preview is not available due to missing webkitgtk2.
- **macOS**: not tested

# Installation

1. Download the latest `jlc-kicad-lib-loader-*-pcm.zip` archive from [Releases page](https://github.com/dsa-t/jlc-kicad-lib-loader/releases).

2. Open PCM in KiCad, click "Install from File...", then choose the downloaded `-pcm` archive:

   ![image](https://github.com/user-attachments/assets/debae118-1292-498a-81f2-29fdc2cf455d)

## To support importing encrypted data

### Windows

3. Open "KiCad x.x Command Prompt":

   ![image](https://github.com/user-attachments/assets/9975de9a-d1cc-4ee7-94b8-11fb492b8b77)

4. Execute `pip install pycryptodome`

   ![image](https://github.com/user-attachments/assets/1abcd9ed-7358-4508-a9fb-75d2bc9bb2a1)

### Debian/Ubuntu

```
sudo apt install python3-pycryptodome
```

### Flatpak

```
flatpak run --command=pip org.kicad.KiCad install pycryptodome
```

### Other OSes

```
pip install pycryptodome
```

### Mac OS

KiCad does NOT use the system Python (/usr/bin/python3).
It comes with a built-in Python located inside the application.

The path to Python KiCad:

```
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3

```

Check versions

```
KPY="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
"$KPY" -V
```

Installing pycryptodome

```
pip install pycryptodome   
```
Checking the result
```
"$KPY" -c "from Crypto.Cipher import AES; print('pycryptodome OK')"
```
Если вывод:
```
pycryptodome OK
```
everything is set up correctly.

#### Installing certifi

On macOS, Python inside KiCad does not see the system certificate store, which causes the following error:

```
SSL: CERTIFICATE_VERIFY_FAILED
```
Installing certifi
```
"$KPY" -m pip install --user --upgrade certifi
```

Check:
```
"$KPY" -c "import certifi; print(certifi.where())"
```



# Library setup

The plugin now automatically manages library configuration:

- **Library Name Storage**: The library name is saved in a `jlc-kicad-lib-loader.ini` file in your project directory and will be remembered for future use.
- **Automatic Library Table Addition**: When downloading components, if the library is not found in your project-specific Symbol/Footprint library tables, the plugin will prompt you to add it automatically.

## Manual Library Setup (if needed)

If you need to manually add the .elibz library to your Symbol/Footprint library tables:

![image](https://github.com/user-attachments/assets/45583737-6747-4aa8-975c-2a90a6f192d6)

### Symbol library table:

![image](https://github.com/user-attachments/assets/a3ff3856-5637-46da-8349-0b965986680f)

### Footprint library table:

![image](https://github.com/user-attachments/assets/8512a77f-95e5-4d4f-bba6-4a2b5660e218)
