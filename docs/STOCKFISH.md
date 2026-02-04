# 🔧 Guía de Instalación y Configuración de Stockfish

## ¿Qué es Stockfish?

**Stockfish** es el motor de ajedrez de código abierto más poderoso del mundo. Es utilizado por:
- Chess.com y Lichess (plataformas online)
- Aplicaciones de escritorio profesionales
- Análisis y entrenamiento

Tu proyecto ahora lo integra para:
- ✅ **Modo Clásico**: Jugador vs Máquina inteligente
- ✅ **Modo Sombras**: IA del Boss más estratégica
- ✅ **Análisis**: Sugerencias de movimientos

---

## 📥 Instalación por Sistema Operativo

### 🪟 Windows

#### Opción 1: Descargar ejecutable (RECOMENDADO)

1. **Descarga el binario compilado**:
   - Visita: https://stockfishchess.org/download/
   - Selecciona la **versión Windows más reciente** (ej: Stockfish 16)
   - Descarga el `.zip`

2. **Extrae el archivo**:
   - Descomprime en una carpeta del proyecto
   - Opción A: `e:\GIT\Ajedrez\stockfish\` (PREFERIDO)
   - Opción B: `e:\GIT\Ajedrez\bin\`
   - Opción C: Cualquier carpeta en tu PATH

3. **Verifica la instalación**:
   ```powershell
   # En PowerShell, desde la carpeta donde extrajiste
   .\stockfish.exe
   # Deberías ver el prompt: "Stockfish 16 by..."
   # Escribe 'quit' para salir
   ```

#### Opción 2: Instalar vía Chocolatey (si tienes)

```powershell
choco install stockfish
```

---

### 🐧 Linux (Ubuntu/Debian)

#### Instalación vía package manager

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install stockfish

# Fedora
sudo dnf install stockfish

# Arch
sudo pacman -S stockfish

# Verificar instalación
stockfish
```

---

### 🍎 macOS

#### Instalación vía Homebrew

```bash
brew install stockfish

# Verificar instalación
stockfish
```

---

## 📂 Estructura de Carpetas - Cómo Organizar Stockfish

El código busca Stockfish automáticamente en este orden:

```
1. PATH del sistema (si está instalado globalmente)
2. ./stockfish/stockfish        ← PREFERIDA por este proyecto
3. ./bin/stockfish
4. ./engines/stockfish
5. Variantes en ./stockfish/
```

### ✅ Estructura RECOMENDADA:

```
e:\GIT\Ajedrez\
├── main.py
├── motor_ajedrez.py          ← NUEVO
├── requirements.txt
├── stockfish/                ← CREAR ESTA CARPETA
│   └── stockfish.exe         ← PEGA AQUI EL BINARIO
├── ajedrez_clasico/
├── ajedrez_sombras/
├── docs/
└── images/
```

**Pasos:**

1. Crea la carpeta `stockfish` en la raíz del proyecto:
   ```powershell
   mkdir e:\GIT\Ajedrez\stockfish
   ```

2. Descarga el `.zip` de Stockfish desde https://stockfishchess.org/download/

3. Extrae `stockfish.exe` (Windows) o `stockfish` (Linux/Mac) en esa carpeta

4. ¡Listo! El código lo detectará automáticamente

---

## 🔍 Verificar que Funciona

### Desde Python

```python
import sys
import os
sys.path.insert(0, r'e:\GIT\Ajedrez')

from motor_ajedrez import MotorAjedrez, NivelDificultad

# Crear motor
motor = MotorAjedrez(nivel=NivelDificultad.MEDIO)

if motor.disponible:
    print("✓ Stockfish conectado exitosamente")
else:
    print("✗ Stockfish NO encontrado")

motor.cerrar()
```

### Desde terminal

```powershell
# Windows
e:\GIT\Ajedrez\stockfish\stockfish.exe

# Linux/Mac
stockfish

# Deberías ver:
# Stockfish 16 by T. Romstad, M. Costalba, J. Kiiski, G. Linscott
# id name Stockfish 16
# id author T. Romstad, M. Costalba, J. Kiiski, G. Linscott
# option name Threads type spin default 1 min 1 max 512
# ...
# Escribe: quit
```

---

## 🎮 Niveles de Dificultad

En el código, puedes ajustar el nivel:

```python
from motor_ajedrez import NivelDificultad

NivelDificultad.FACIL      # 100ms  - Rápido pero débil
NivelDificultad.MEDIO      # 500ms  - Balance (PREDETERMINADO)
NivelDificultad.DIFICIL    # 2000ms - Muy fuerte
NivelDificultad.ANALISIS   # 5000ms - Análisis profundo
```

**Para cambiar en `main.py`:**

```python
# Línea ~145 en main.py
motor = MotorAjedrez(nivel=NivelDificultad.DIFICIL)  # Cambiar a DIFICIL
```

---

## ⚠️ Solución de Problemas

### ❌ "Stockfish no encontrado"

**Causa**: No instaló Stockfish o está en una ubicación que el código no busca

**Solución**:
1. Descargue desde https://stockfishchess.org/download/
2. Coloque en `e:\GIT\Ajedrez\stockfish\`
3. Reinicie Python

---

### ❌ "Permission denied" (Linux/Mac)

**Causa**: El binario no tiene permisos de ejecución

**Solución**:
```bash
chmod +x /ruta/al/stockfish
```

---

### ❌ "Engine quit unexpectedly"

**Causa**: Versión corrupta o incompatible de Stockfish

**Solución**:
1. Descargue la versión oficial más reciente
2. Reemplace el binario anterior
3. Reinicie Python

---

### ❌ El juego se congela durante los movimientos

**Nota**: ¡Esto ya está SOLUCIONADO! La versión nueva usa **threading asincrónico**

- Antes: Se congelaba mientras Stockfish pensaba
- Ahora: La UI sigue responsiva, muestra "🤖 Stockfish pensando..."

---

## 📊 Parámetros Avanzados

Estos son las opciones UCI que Stockfish soporta (si quieres modificar más adelante):

```
Threads              - Número de hilos CPU (predeterminado: 1)
Hash                 - Memoria para tabla transposicional (MB)
MultiPV              - Mostrar múltiples líneas principales
Contempt             - Preferencia por complicaciones
```

**Ejemplo (futuro):**
```python
# En motor_ajedrez.py, podrías agregar:
self.engine.configure({"Threads": 4, "Hash": 256})
```

---

## 📚 Enlaces Útiles

- **Sitio Oficial**: https://stockfishchess.org/
- **Descargas**: https://stockfishchess.org/download/
- **Documentación UCI**: https://en.wikipedia.org/wiki/Universal_Chess_Interface
- **GitHub**: https://github.com/official-stockfish/Stockfish

---

## ✅ Checklist Final

- [ ] Descargué Stockfish desde https://stockfishchess.org/download/
- [ ] Creé carpeta `e:\GIT\Ajedrez\stockfish\`
- [ ] Extraje `stockfish.exe` (Windows) o `stockfish` (Linux/Mac)
- [ ] Ejecuté `stockfish` desde terminal y vi el prompt
- [ ] Probé el código Python desde arriba
- [ ] Ejecuté `main.py` y seleccioné "Jugador vs Máquina (Stockfish)"
- [ ] ¡El juego funciona sin congelarse!

---

**¡Listo!** Ahora tu proyecto tiene integración profesional de Stockfish. 🚀
