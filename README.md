<p align="center">
  <img src="https://img.shields.io/badge/version-v0.1.8-blue" alt="Version v0.1.8"/>
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
- [📝 Changelog](#-changelog)
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

### Errores específicos de Windows ya conocidos

| Síntoma en pantalla                                      | Causa real | Solución |
| -------------------------------------------------------- | ---------- | -------- |
| `No se encontro Python` o ventana se cierra al toque     | El `python.exe` que Windows encuentra es el **stub de Microsoft Store** (no funciona) | Reinstala Python desde [python.org](https://www.python.org/downloads/) desmarcando "Microsoft Store" y desmarcando el stub de la Tienda. O usá la versión que detecta el .bat en `%LOCALAPPDATA%\Programs\Python\Python3XX\`. |
| `No se esperaba ... en este momento.`                    | El `.bat` tenía `...` al final de un `echo` — `cmd` lo lee como wildcard | Ya arreglado en v0.1.3. Si reaparece, mandá el `last_run.log`. |
| `La sintaxis del comando no es correcta.`                | El `.bat` tenía `|` al final de un `echo` — `cmd` lo lee como operador de pipe | Ya arreglado en v0.1.4. Si reaparece, mandá el `last_run.log`. |
| Crash con código `-1073741819` al dar **Reproducir**     | El thread del player tocaba widgets de Qt directamente | Ya arreglado en v0.1.5 con `Signal.emit()`. Si reaparece, mandá el `last_run.log`. |
| El `.bat` se abre y se cierra al toque sin ver nada       | Muchas causas posibles; siempre hay un `last_run.log` con lo que pasó | Doble clic en `diagnostico.bat` → me mandás la salida. |

### Problemas generales

| Problema                                      | Solución |
| --------------------------------------------- | -------- |
| "Python no se reconoce como comando"          | Reinstala Python tildando **"Add Python to PATH"**. O ejecutá `diagnostico.bat` para ver qué encontró. |
| La app no detecta clicks                      | Probá ejecutarla como **Administrador** (clic derecho en `ejecutar.bat` → "Ejecutar como administrador") |
| El `.exe` lo bloquea el antivirus             | Agregá excepción para la carpeta `dist\` |
| No se ve el efecto glass                      | Confirmá que estés en **Windows 11** (Mica solo funciona ahí) |
| F9 no responde                                | Algún programa está capturando F9. Cambialo en el código (`src/core/hotkey.py`) |
| `pip install` falla                           | Sin internet, firewall bloqueando, o falta de permisos. Probá como Administrador. |
| Ventana de cmd desaparece y no puedo leer el error | Siempre hay un `last_run.log` en la carpeta. Ábrelo con el Bloc de notas. |

### ¿Cómo pedir ayuda?

1. Doble clic en `diagnostico.bat` → me mandás la salida completa.
2. Abrí `last_run.log` con el Bloc de notas → me mandás su contenido.
3. Contame qué estabas haciendo cuando pasó el error.

---

## 📝 Changelog

### v0.1.8 — UI redesign: solid dark theme (2026-06-01)
- **Redesign:** Eliminado el efecto Mica/Acrylic translúcido que hacía la ventana "blanca" según el wallpaper.
- **Redesign:** Nueva paleta sólida oscura `#0d1117` (inspirada GitHub Dark) con alto contraste.
- **Redesign:** Colores acento desaturados — azul `#58a6ff`, rojo `#da3633`, verde `#3fb950`.
- **Removed:** `WA_TranslucentBackground`, `DwmSetWindowAttribute`, toda la lógica Mica/Acrylic.
- **Fix:** Todos los textos tienen contraste ≥4.5:1 incluso los secundarios/muted.
- **Fix:** `GlassCard` renombrado a `panelCard` en QSS, bordes visibles, fondos sólidos.
- **Fix:** Botones con estados hover/pressed/disabled claramente diferenciados.
- **Fix:** StatusPill, listas, inputs, scrollbars con fondos y bordes sólidos visibles.

### v0.1.7 — Crash diagnostics + thread-safety hardening (2026-06-01)
- **Add:** `faulthandler` + `sys.excepthook` en `main.py` — captura stack traces completos en `crash_traceback.log` ante segfaults o excepciones no manejadas.
- **Fix:** `_handle_hotkey_cancel` ahora deferido al UI thread via `QTimer.singleShot(0, ...)`, igual que `_handle_hotkey_play` — elimina race condition potencial con el thread de pynput.
- **Fix:** `recorder.stop()` ya no bloquea el UI thread — detiene el listener de pynput en un daemon thread separado.
- **Fix:** Selector inválido `#titleBtn#close` (ID duplicado en QSS) reemplazado por property selector `[class="close"]`.
- **Fix:** Se eliminó `setStyleSheet()` redundante en `_btn_load` que podía confundir al parser de QSS.
- **Fix:** `ejecutar.bat` ahora prefiere Python 3.12 sobre 3.13 por estabilidad probada con PySide6.
- **Add:** `crash_traceback.log` en `.gitignore` (cubierto por `*.log`).

### v0.1.6 — Hard-won lessons documentation
- **Docs:** Documentación de los 7 errores más costosos en `AGENTS.md` + limpieza de `README.md`.
- **Note:** Sin cambios de código. Crashes existentes desde v0.1.5 (solo se documentaron).

### v0.1.5 — Thread-safety con Qt Signals
- **Fix:** Crash con código `-1073741819` al dar **Reproducir**.
- **Causa:** El thread del player tocaba widgets de Qt directamente.
- **Solución:** `_PlayerBridge(QObject)` con Signals que enrutan al thread UI.

### v0.1.4 — Fix pipe character en .bat
- **Fix:** `La sintaxis del comando no es correcta` al ejecutar `ejecutar.bat`.
- **Causa:** `|` (pipe operator) al final de un `echo`.
- **Solución:** Eliminado. Todos los `.bat` ahora son ASCII puro.

### v0.1.3 — Fix wildcard en .bat
- **Fix:** `No se esperaba ... en este momento` al ejecutar.
- **Causa:** `...` al final de un `echo` — `cmd` lo lee como wildcard.
- **Solución:** Reemplazados por caracteres no especiales.

### v0.1.2 — Logging a archivo y wrapper
- **Add:** `last_run.log` con cada paso timestamped.
- **Add:** `iniciar.cmd` — wrapper que fuerza ventana abierta.
- **Add:** `diagnostico.bat` — script de soporte.

### v0.1.1 — Detección de Python real
- **Fix:** `ejecutar.bat` se cerraba al toque.
- **Causa:** `where python` resolvía al stub de Microsoft Store.
- **Solución:** Búsqueda en `%LOCALAPPDATA%\Programs\Python\Python*` con prioridad por versión.

### v0.1.0 — Lanzamiento inicial
- Grabación y reproducción de mouse con timing real
- Formato `.mrcd` (JSON)
- UI dark glass con Mica/Acrylic en Win11
- Atajo global F9
- Build a `.exe` con PyInstaller

---

## 🗺️ Roadmap

### v0.1.0 (inicial) ✅
- [x] Estructura del proyecto estilo CinePolys
- [x] Captura de mouse (move, click, scroll) con timestamps
- [x] Reproducción con timing real
- [x] Save/load en formato `.mrcd` (JSON)
- [x] UI dark glass con Mica/Acrylic en Win11
- [x] Atajo global F9 para reproducir última grabación
- [x] Build a `.exe` con PyInstaller
- [x] `ejecutar.bat` y `compilar.bat` de doble clic

### v0.1.x (estabilización del launcher) ✅
- [x] **v0.1.1** — Detección robusta de Python (skipea el stub de Microsoft Store)
- [x] **v0.1.2** — Logging a `last_run.log` + wrapper `iniciar.cmd` con `cmd /k`
- [x] **v0.1.3** — Fix `No se esperaba ...` (caracteres especiales en .bat)
- [x] **v0.1.4** — Fix `La sintaxis del comando no es correcta` (pipe operator)
- [x] **v0.1.5** — Fix access violation `0xC0000005` con Qt Signals thread-safe

### v0.2.0 (próximo)
- [ ] Loop / repetir N veces
- [ ] Atajo configurable desde la UI
- [ ] Indicador visual al reproducir (overlay sutil en pantalla)
- [ ] Editar nombre de recordings desde la lista
- [ ] Eliminar grabaciones desde la lista (clic derecho → eliminar)

### v0.3.0 (ideas)
- [ ] Captura de teclado (no solo mouse)
- [ ] Velocidad de reproducción (0.5x, 1x, 2x)
- [ ] Tray icon (minimizar a bandeja del sistema)
- [ ] Tema claro opcional

### Seguridad / Robustez
- [x] Cancelar reproducción con ESC desde cualquier ventana (v0.1.0)
- [x] Validación de JSON al cargar `.mrcd` (v0.1.0)
- [ ] Manejo de coordenadas fuera de pantalla (clamp a límites del monitor)

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).
