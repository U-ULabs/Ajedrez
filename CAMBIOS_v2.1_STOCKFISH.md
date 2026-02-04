# 📋 Documento de Cambios - Integración de Stockfish v2.1

**Fecha**: 3 de febrero de 2026  
**Versión**: 2.1  
**Cambio Principal**: Integración centralizada y optimizada de Stockfish con threading asincrónico

---

## 🎯 Resumen de Mejoras

| Aspecto | Antes (v2.0) | Después (v2.1) | Beneficio |
|--------|------------|---------------|-----------|
| **Integración Motor** | En `reglas.py` (disperso) | `motor_ajedrez.py` (centralizado) | ✅ Reutilizable en todos los modos |
| **UI en juego_vs_maquina** | ❌ Se congela mientras Stockfish piensa | ✅ Async con threading | ⚡ Interfaz responsiva |
| **Niveles dificultad** | Solo "fácil/medio/difícil" strings | `NivelDificultad` enum robusto | 🎮 Escalable y tipado |
| **IA Sombras** | IA heurística básica | + Integración opcional Stockfish | 🤖 Boss más estratégico |
| **Detección Motor** | Manual en reglas.py | Automática centralizada | 🔍 Menos configuración |
| **Documentación** | Mínima | `docs/STOCKFISH.md` completa | 📖 Guía profesional |

---

## 📁 Archivos Nuevos

### 1. **`motor_ajedrez.py`** (NUEVO)
Módulo centralizado para gestionar Stockfish

**Clases principales:**

```python
class MotorAjedrez:
    """Interfaz profesional para Stockfish UCI"""
    - Detección automática del binario
    - Búsqueda bloqueante y asincrónica
    - Thread-safe para operaciones paralelas
    - Gestión robusta de errores

class NivelDificultad(Enum):
    FACIL = 100ms
    MEDIO = 500ms         # Predeterminado
    DIFICIL = 2000ms
    ANALISIS = 5000ms

class ResultadoMotor:
    """Encapsula resultados de búsqueda"""
    - movimiento_lan
    - evaluacion (centipeones)
    - profundidad
    - error
```

**Características:**
- ✅ Búsqueda bloqueante: `motor.buscar_movimiento()`
- ✅ Búsqueda async: `motor.buscar_movimiento_async(callback)`
- ✅ Estado de máquina: `motor.esta_calculando()`
- ✅ Conversión FEN automática

---

### 2. **`docs/STOCKFISH.md`** (NUEVO)
Guía completa de instalación y configuración

**Secciones:**
- Qué es Stockfish
- Instalación por SO (Windows/Linux/macOS)
- Estructura de carpetas recomendada
- Verificación de funcionamiento
- Solución de problemas
- Parámetros avanzados
- Checklist final

---

## 🔄 Archivos Modificados

### 1. **`main.py`** v2.0 → v2.1

**Cambios en importaciones (línea 1-16):**
```python
# NUEVO: Importar motor centralizado
from motor_ajedrez import MotorAjedrez, NivelDificultad, EstadoMotor

# REMOVIDO: ya no necesitamos sugerir_movimiento de reglas.py
```

**Cambios en `juego_vs_maquina()` (línea 139-219):**

**Antes (v2.0):**
```python
# Bloqueante - congelaba la interfaz
if interfaz.tablero.turno == Color.NEGRO:
    interfaz.mensaje_estado = "Pensando..."
    interfaz.dibujar_tablero(seleccionado)
    pygame.display.flip()
    
    # Aquí se bloqueaba todo
    lan = sugerir_movimiento(...)  # ← BLOQUEANTE
    coords = _lan_a_coords(lan) if lan else None
    if coords:
        ...
```

**Después (v2.1):**
```python
# Asincrónico - UI sigue responsiva
if interfaz.tablero.turno == Color.NEGRO:
    if not motor.esta_calculando() and not movimiento_ia_listo:
        # Iniciar búsqueda en hilo separado
        motor.buscar_movimiento_async(
            interfaz.tablero.casillas,
            interfaz.tablero.turno,
            callback_movimiento_ia  # ← Se llama cuando está listo
        )
        interfaz.mensaje_estado = "🤖 Stockfish pensando..."
    
    # Mientras tanto, la UI sigue activa
    if movimiento_ia_listo and resultado_ia and resultado_ia.exitoso:
        lan = resultado_ia.movimiento_lan
        # ... procesar movimiento
```

**Ventajas:**
- ✅ No se congela la ventana
- ✅ Se puede cerrar mientras calcula
- ✅ Muestra estado visual ("🤖 pensando...")
- ✅ Manejo robusto de errores

---

### 2. **`ajedrez_sombras/ia_sombras.py`** v2.0 → v2.1

**Cambios en inicialización (línea 1-50):**
```python
# NUEVO: Importar motor opcional
from motor_ajedrez import MotorAjedrez, NivelDificultad

class IASombras:
    def __init__(self, tablero, usar_stockfish: bool = True):
        # NUEVO: Inicializa motor si está disponible
        self.motor = None
        if self.usar_stockfish and STOCKFISH_DISPONIBLE:
            self.motor = MotorAjedrez(nivel=NivelDificultad.FACIL)
```

**Cambios en lógica de movimientos (línea 52-95):**

**Antes (v2.0):**
```python
def calcular_movimiento(self):
    # Prioridad 1: Ataque
    # Prioridad 2: Movimiento táctico
    # Prioridad 3: Aleatorio
```

**Después (v2.1):**
```python
def calcular_movimiento(self):
    # Prioridad 1: Ataque
    # Prioridad 2: Análisis Stockfish (NUEVO)
    #     ↳ _obtener_movimiento_stockfish()
    # Prioridad 3: Movimiento táctico
    # Prioridad 4: Aleatorio
    
    # Si Stockfish falla, fallback automático a heurísticas
```

**Método nuevo:** `_obtener_movimiento_stockfish()`
- Análisis defensivo/ofensivo según distancia al jugador
- Fallback silencioso si hay errores
- No rompe el juego si Stockfish no está disponible

---

### 3. **`requirements.txt`** v2.0 → v2.1

**Cambios:**
```diff
- # ==============================================================================
- # DEPENDENCIAS DEL PROYECTO AJEDREZ v2.0
- ==============================================================================
- # DEPENDENCIAS DEL PROYECTO AJEDREZ v2.1
+ # CAMBIOS v2.1:
+ # - Integración centralizada de Stockfish (motor_ajedrez.py)
+ # - Threading asincrónico para UI responsiva
+ # - IA Sombras mejorada con análisis estratégico
+ # Ver: docs/STOCKFISH.md para instalación del motor UCI

- # python-chess - Validación de movimientos, generación de FEN, integración UCI
+ # python-chess - Validación de movimientos, generación de FEN, integración UCI
+ # Nota: Stockfish debe descargarse por separado desde https://stockfishchess.org/download/
```

**Nota:** No se agregaron dependencias pip nuevas (python-chess ya estaba)

---

## 🔧 Cambios Técnicos Detallados

### Threading en `juego_vs_maquina()`

**Problema v2.0:**
```python
# La búsqueda de Stockfish bloqueaba el hilo principal
while True:
    if turno_ia:
        lan = sugerir_movimiento(...)  # ← Espera X segundos aquí
        # La ventana está congelada, no responde eventos
```

**Solución v2.1:**
```python
# La búsqueda ocurre en hilo separado
def callback_movimiento_ia(resultado):
    nonlocal movimiento_ia_listo, resultado_ia
    resultado_ia = resultado
    movimiento_ia_listo = True

while True:
    if turno_ia and not motor.esta_calculando():
        # Inicia búsqueda en hilo separado
        motor.buscar_movimiento_async(..., callback_movimiento_ia)
        # El bucle SIGUE AQUÍ, no espera
        interfaz.dibujar_tablero()  # ← Responde eventos
    
    if movimiento_ia_listo:
        # El resultado está listo, procesar
        lan = resultado_ia.movimiento_lan
```

---

### Detección Automática de Stockfish

**Orden de búsqueda en `motor_ajedrez.py`:**

```python
def _detectar_stockfish(self):
    # 1. PATH del sistema
    #    ↳ shutil.which("stockfish.exe")
    
    # 2. Directorios locales
    #    ↳ ./stockfish/stockfish.exe  ← PREFERIDO
    #    ↳ ./bin/stockfish.exe
    #    ↳ ./engines/stockfish.exe
    
    # 3. Variantes en carpeta stockfish/
    #    ↳ Lista archivos y busca "stockfish*"
```

**Beneficio:** Solo coloca el binario en `./stockfish/` y ¡funciona!

---

### Conversión FEN Centralizada

**Antes:** Duplicada entre `reglas.py` y `motor_ajedrez.py`  
**Después:** Centralizada en `MotorAjedrez._tablero_a_fen()`

```python
# Una única fuente de verdad para conversión FEN
class MotorAjedrez:
    def _tablero_a_fen(self, casillas, turno):
        # Lógica centralizada
        # Reutilizada en buscar_movimiento() y buscar_movimiento_async()
```

---

## 🎮 Cómo Usar (Para el Usuario)

### 1. **Instalación Rápida (5 minutos)**

```powershell
# 1. Descargar Stockfish desde:
# https://stockfishchess.org/download/

# 2. Crear carpeta en proyecto
mkdir e:\GIT\Ajedrez\stockfish

# 3. Extraer stockfish.exe en esa carpeta
# e:\GIT\Ajedrez\stockfish\stockfish.exe

# 4. ¡Listo! Ejecutar main.py
python main.py
```

### 2. **Seleccionar Modo**
```
1. AJEDREZ CLÁSICO
   ↓ Seleccionar "Jugador vs Máquina (Stockfish)"
```

### 3. **Jugar**
```
- Juega con Blancas
- Stockfish responde automáticamente
- UI sigue responsiva durante el análisis
```

---

## ⚠️ Consideraciones Importantes

### Compatibilidad Hacia Atrás
✅ **Retrocompatible 100%**
- `reglas.py` sigue funcionando
- `sugerir_movimiento()` aún disponible
- Métodos antiguos no removidos

### Si Stockfish No Está Disponible
✅ **El juego SIGUE FUNCIONANDO**
- Cae a IA aleatoria
- Ajedrez Sombras usa heurísticas
- Aviso amistoso en consola

### Thread-Safety
✅ **Uso seguro de threading**
- Lock en `_lock` para acceso a `resultado_actual`
- Métodos async no bloquean
- Limpieza adecuada de recursos

---

## 📊 Antes y Después - Comparativa

### UX: Jugador vs Máquina

| Acción | v2.0 | v2.1 |
|--------|------|------|
| Click en pieza | ✅ Inmediato | ✅ Inmediato |
| Stockfish piensa | ❌ Congelado | ✅ Muestra "🤖 pensando..." |
| Cerrar ventana | ❌ Espera a terminar | ✅ Responde inmediatamente |
| Mover mientras calcula | ❌ No se puede | ✅ Se puede |

---

## 🚀 Próximos Pasos Sugeridos

1. **Análisis en vivo** (futuro v2.2)
   ```python
   # Mostrar evaluación de Stockfish mientras juega
   evaluacion = resultado.evaluacion  # Ya está disponible
   ```

2. **Selección de nivel en menú** (futuro v2.2)
   ```python
   # Menu con opciones: Fácil / Medio / Difícil
   menu_nivel = Menu(["Fácil", "Medio", "Difícil"])
   nivel = menu_nivel.loop()
   ```

3. **Análisis post-juego** (futuro v2.3)
   ```python
   # Mostrar mejores movimientos al finalizar
   for movimiento_historico in historial:
       evaluacion = motor.analizar(movimiento_historico)
   ```

---

## 📚 Documentación Relacionada

- [📖 docs/STOCKFISH.md](docs/STOCKFISH.md) - Instalación completa
- [🔧 README.md](README.md) - Visión general del proyecto
- [📚 Wiki](wiki/Home.md) - Documentación completa

---

## ✅ Testing Recomendado

```python
# test_motor_ajedrez.py
from motor_ajedrez import MotorAjedrez, NivelDificultad

# Test 1: Detección automática
motor = MotorAjedrez()
assert motor.disponible, "Stockfish no detectado"

# Test 2: Búsqueda bloqueante
movimiento = motor.buscar_movimiento({}, Color.BLANCO)
assert movimiento is None or len(movimiento) == 4

# Test 3: Búsqueda async
resultado_listo = False
def callback(r):
    global resultado_listo
    resultado_listo = True

motor.buscar_movimiento_async({}, Color.BLANCO, callback)
# ... esperar callback

motor.cerrar()
```

---

**¡Integración completada!** El proyecto ahora tiene una implementación profesional de Stockfish. 🎉
