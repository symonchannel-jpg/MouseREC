<p align="center">
  <img src="https://img.shields.io/badge/Windows%2011-0078D4?logo=windows11&logoColor=white" alt="Windows 11"/>
  <img src="https://img.shields.io/badge/Python%203.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/PySide6-41CD52?logo=qt&logoColor=white" alt="PySide6"/>
  <img src="https://img.shields.io/badge/pynput-FFD43B?logo=python&logoColor=black" alt="pynput"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/>
</p>

<p align="center">
  <h1 align="center">MouseRecorder — Graba y automatiza tu mouse</h1>
</p>

<p align="center">
  <img src="assets/banner.png" alt="MouseRecorder screenshot" width="800"/>
</p>

<p align="center">
  App de escritorio minimalista para Windows 11. Grabá los movimientos y clicks de tu mouse, guardá la grabación y reproducila con un atajo de teclado.
</p>

---

## 📑 Tabla de Contenidos

- [✨ Funciones](#-funciones)
- [🎯 Objetivo](#-objetivo)
- [🚀 Inicio Rápido](#-inicio-rápido)
  - [Requisitos](#requisitos)
  - [Pasos](#pasos)
- [🎮 Cómo usar](#-cómo-usar)
- [📚 Documentación](#-documentación)
  - [Stack Técnico](#stack-técnico)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Formato de Archivo .mrcd](#formato-de-archivo-mrcd)
- [🔧 Solución de Problemas](#-solución-de-problemas)
- [🗺️ Roadmap](#️-roadmap)

---

## ✨ Funciones

| Función              | Descripción |
| -------------------- | ----------- |
| 🔴 **Grabar Mouse**  | Captura movimientos, clicks y scroll del mouse en tiempo real |
| ⏹️ **Detener**       | Termina la grabación actual |
| ▶️ **Reproducir**    | Reproduce la última grabación con timing exacto |
| 💾 **Guardar**       | Exporta la grabación como archivo `.mrcd` reusable |
| 📂 **Cargar**        | Importa una grabación `.mrcd` desde disco |
| ⌨️ **Atajo Global**  | F9 = reproducir última grabación desde cualquier app |
| 🎨 **Glass Moderno** | Diseño dark con Mica/Acrylic nativo de Windows 11 |

---

## 🎯 Objetivo

Automatizar acciones repetitivas del mouse sin necesidad de software complejo. Ideal para:

- Tareas mecánicas en hojas de cálculo
- Rellenar formularios
- Repetir secuencias de clicks en aplicaciones
- Demo de flujos de UI

---

## 🚀 Inicio Rápido

### Requisitos

- **Windows 11** (para Mica/Acrylic real — funciona en Win10 con translucency básica)
- **Python 3.11 o superior** (descargar de [python.org](https://www.python.org/downloads/))
  - ⚠️ Al instalar, tildar **"Add Python to PATH"**

### Pasos

1. **Abrí la carpeta del proyecto** en el explorador de Windows:
   ```
   H:\OpenCode_Proyectos\2026-05\08_MouseRecorder
   ```

2. **Doble clic en `ejecutar.bat`**
   - La primera vez crea el entorno virtual e instala las dependencias (tarda 1-2 minutos).
   - Las siguientes veces abre la app directamente.
   - Si algo falla, el `.bat` te avisa en pantalla y se queda pausado para que veas el error.

3. **Listo.** La ventana de MouseRecorder se abre.

> Si querés generar un `.exe` portable: doble clic en `compilar.bat` → queda en `dist\MouseRecorder.exe`.

---

## 🎮 Cómo usar

| Acción                     | Cómo |
| -------------------------- | ---- |
| Empezar a grabar           | Clic en **🔴 Grabar** (o el botón se pone rojo) |
| Detener grabación          | Clic en **⏹️ Detener** |
| Reproducir última grabada  | Clic en **▶️ Reproducir** |
| Guardar en disco           | Clic en **💾 Guardar** → escribí un nombre → Enter |
| Cargar desde disco         | Clic en **📂 Cargar** → elegí un `.mrcd` |
| Reproducir con teclado     | Presioná **F9** en cualquier momento |
| Cancelar reproducción      | Presioná **ESC** |

Los archivos se guardan en la carpeta `recordings\` junto al ejecutable.

---

## 📚 Documentación

### Stack Técnico

| Capa            | Tecnología                        |
| --------------- | --------------------------------- |
| Lenguaje        | Python 3.11+                      |
| UI              | PySide6 (Qt 6)                    |
| Glass / Mica    | DwmSetWindowAttribute (ctypes)    |
| Mouse Hooks     | pynput                            |
| Empaquetado     | PyInstaller → `.exe` standalone   |
| Formato datos   | JSON (`.mrcd`)                    |

### Estructura del Proyecto

```
08_MouseRecorder/
├── main.py                 # Punto de entrada
├── ejecutar.bat            # Doble clic → prepara venv y abre la app
├── compilar.bat            # Doble clic → genera MouseRecorder.exe
├── diagnostico.bat         # Doble clic → muestra info de Python/venv/paquetes
├── assets/
│   ├── icon.ico            # Icono de la app
│   └── banner.png          # Banner del README
├── recordings/             # Archivos .mrcd guardados
│   └── .gitkeep
└── src/
    ├── ui/
    │   ├── app.py          # Ventana principal frameless con Mica
    │   ├── theme.py        # Paleta dark + QSS glass
    │   └── widgets.py      # GlassCard, GlowButton
    ├── core/
    │   ├── recorder.py     # Captura eventos de mouse (pynput)
    │   ├── player.py       # Reproduce eventos con timing real
    │   ├── storage.py      # Save/load .mrcd
    │   └── hotkey.py       # Listener global de F9
    └── utils/
        └── paths.py        # Rutas recordings/ y assets/
```

### Formato de Archivo .mrcd

```json
{
  "version": 1,
  "name": "mi macro",
  "created_at": "2026-06-01T12:00:00",
  "events": [
    {"t": 0,   "type": "move",   "x": 100, "y": 200},
    {"t": 150, "type": "click",  "x": 100, "y": 200, "button": "left"},
    {"t": 300, "type": "scroll", "x": 100, "y": 200, "dx": 0, "dy": -1}
  ]
}
```

- `t` = milisegundos desde el inicio de la grabación
- Tipos: `move`, `click`, `scroll`
- Editable a mano si querés ajustar el timing

---

## 🔧 Solución de Problemas

| Problema                                      | Solución |
| --------------------------------------------- | -------- |
| "Python no se reconoce como comando"          | Reinstala Python tildando **"Add Python to PATH"**. O ejecutá `diagnostico.bat` para ver qué encontró. |
| La app no detecta clicks                      | Probá ejecutarla como **Administrador** (clic derecho en `ejecutar.bat` → "Ejecutar como administrador") |
| El `.exe` lo bloquea el antivirus             | Agregá excepción para la carpeta `dist\` |
| No se ve el efecto glass                      | Confirmá que estés en **Windows 11** (Mica solo funciona ahí) |
| F9 no responde                                | Algún programa está capturando F9. Cambialo en el código (`src/core/hotkey.py`) |
| El `.bat` se abre y cierra rápido             | Ejecutá `diagnostico.bat` primero y mandame la salida. |

---

## 🗺️ Roadmap

### v0.1.0 (inicial)
- [x] Estructura del proyecto estilo CinePolys
- [x] Captura de mouse (move, click, scroll) con timestamps
- [x] Reproducción con timing real
- [x] Save/load en formato `.mrcd` (JSON)
- [x] UI dark glass con Mica/Acrylic en Win11
- [x] Atajo global F9 para reproducir última grabación
- [x] Build a `.exe` con PyInstaller
- [x] `ejecutar.bat` y `compilar.bat` de doble clic

### v0.2.0 (próximo)
- [ ] Loop / repetir N veces
- [ ] Atajo configurable desde la UI
- [ ] Indicador visual al reproducir (overlay sutil en pantalla)
- [ ] Editar nombre de recordings desde la lista

### v0.3.0 (ideas)
- [ ] Captura de teclado (no solo mouse)
- [ ] Velocidad de reproducción (0.5x, 1x, 2x)
- [ ] Tray icon (minimizar a bandeja del sistema)
- [ ] Tema claro opcional

### Seguridad / Robustez
- [ ] Cancelar reproducción con ESC desde cualquier ventana
- [ ] Validación de JSON al cargar `.mrcd`
- [ ] Manejo de coordenadas fuera de pantalla

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).
