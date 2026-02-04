# 🎮 Actualización: Selección de Motor de IA

**Fecha:** 3 de febrero de 2026  
**Cambio:** Menú de selección de tipo de IA antes de jugar

---

## 🔧 ¿Qué Cambió?

### Antes (v2.1)
```
AJEDREZ CLÁSICO
  ↓
"Jugador vs Máquina (Stockfish)"
  ↓
Si Stockfish no está → Vuelve al menú sin explicación
```

### Ahora (v2.1.1)
```
AJEDREZ CLÁSICO
  ↓
"Jugador vs Máquina"
  ↓
Submenu:
  ├─ Stockfish (Motor UCI)     ← Requiere instalación
  ├─ IA Aleatoria              ← Siempre disponible
  └─ Volver
```

---

## ✨ Mejoras

| Aspecto | Mejora |
|--------|--------|
| **Selección de motor** | Ahora puedes elegir qué tipo de IA jugar |
| **Fallback automático** | Si Stockfish no está → Muestra aviso y ofrece alternativas |
| **Mensajes claros** | Explica dónde descargar Stockfish y cómo instalarlo |
| **IA Aleatoria** | Opción que siempre funciona sin dependencias |
| **No bloquea** | IA Aleatoria es rápida (no congela la UI) |

---

## 🎯 Flujo Nuevo

### Opción 1: Jugar con Stockfish
```
1. Seleccionar "Jugador vs Máquina"
2. Seleccionar "Stockfish (Motor UCI)"
3. Si Stockfish está instalado:
   ✓ Juega contra Stockfish
   - Muestra "🤖 Stockfish pensando..."
   - UI responsiva (threading async)
4. Si Stockfish NO está:
   ✓ Muestra aviso
   ✓ Ofrece descargar desde https://stockfishchess.org/download/
   ✓ Automáticamente cambia a IA Aleatoria
```

### Opción 2: Jugar con IA Aleatoria
```
1. Seleccionar "Jugador vs Máquina"
2. Seleccionar "IA Aleatoria"
3. ✓ Juega contra IA aleatoria
   - Muestra "🎲 IA Aleatoria pensando..."
   - Rápido (200ms)
   - Funciona siempre
```

---

## 📝 Cambios Técnicos

### 1. Menú Principal Actualizado

**Antes:**
```python
menu_clasico = Menu([
    "Jugador vs Jugador",
    "Partida LAN - Crear Servidor",
    "Partida LAN - Unirse a Servidor",
    "Jugador vs Máquina (Stockfish)",  # ← Específico
    "Volver"
])
```

**Ahora:**
```python
menu_clasico = Menu([
    "Jugador vs Jugador",
    "Partida LAN - Crear Servidor",
    "Partida LAN - Unirse a Servidor",
    "Jugador vs Máquina",              # ← Genérico
    "Volver"
])

# Submenu si selecciona Jugador vs Máquina
menu_ia = Menu([
    "Stockfish (Motor UCI)",
    "IA Aleatoria",
    "Volver"
])

tipo_ia = menu_ia.loop()

if tipo_ia == "Stockfish (Motor UCI)":
    juego_vs_maquina(motor_type="stockfish")
elif tipo_ia == "IA Aleatoria":
    juego_vs_maquina(motor_type="random")
```

### 2. Función `juego_vs_maquina()` Mejorada

**Ahora acepta parámetro `motor_type`:**
```python
def juego_vs_maquina(motor_type: str = "stockfish"):
    """
    Args:
        motor_type: "stockfish" o "random"
    """
    
    # Inicializar según tipo
    if motor_type == "stockfish":
        motor = MotorAjedrez(nivel=NivelDificultad.MEDIO)
        if not motor.disponible:
            print("⚠️  Stockfish no disponible")
            print("   👉 Descarga desde: https://stockfishchess.org/download/")
            print("   👉 Coloca en: ./stockfish/")
            motor_type = "random"  # Fallback
    
    if motor_type == "random":
        print("✓ IA Aleatoria seleccionada")
```

### 3. Nueva Función `_obtener_movimiento_aleatorio()`

```python
def _obtener_movimiento_aleatorio(tablero):
    """Obtiene un movimiento aleatorio legal.
    
    1. Busca todas las piezas del color actual
    2. Obtiene movimientos legales de cada pieza
    3. Elige uno al azar
    
    Returns:
        Tupla (origen, destino) o None
    """
    import random
    
    movimientos_posibles = []
    
    for casilla, pieza in tablero.casillas.items():
        if pieza and pieza.color == tablero.turno:
            movimientos = tablero.obtener_movimientos_legales(casilla)
            for destino in movimientos:
                movimientos_posibles.append((casilla, destino))
    
    if movimientos_posibles:
        return random.choice(movimientos_posibles)
    
    return None
```

### 4. Lógica de Movimiento IA

**Stockfish (Asincrónico):**
```python
if motor_type == "stockfish" and motor_disponible:
    if not motor.esta_calculando() and not movimiento_ia_listo:
        motor.buscar_movimiento_async(...)
        interfaz.mensaje_estado = "🤖 Stockfish pensando..."
    
    if movimiento_ia_listo and resultado_ia.exitoso:
        # Ejecutar movimiento
```

**IA Aleatoria (Bloqueante pero rápido):**
```python
elif motor_type == "random":
    interfaz.mensaje_estado = "🎲 IA Aleatoria pensando..."
    pygame.time.wait(200)  # Delay visual
    
    movimiento = _obtener_movimiento_aleatorio(interfaz.tablero)
    if movimiento:
        # Ejecutar movimiento
```

---

## 🎮 Cómo Usar

### Jugar con Stockfish
```
1. python main.py
2. AJEDREZ CLÁSICO
3. Jugador vs Máquina
4. Stockfish (Motor UCI)
5. (Si está instalado) ¡A jugar!
   (Si no está instalado) Fallback a IA Aleatoria automáticamente
```

### Jugar con IA Aleatoria
```
1. python main.py
2. AJEDREZ CLÁSICO
3. Jugador vs Máquina
4. IA Aleatoria
5. ¡A jugar! (Siempre funciona)
```

---

## 📊 Comportamiento

### Si Stockfish Está Instalado
- Selecciona "Stockfish (Motor UCI)" → Juega contra Stockfish
- UI responsiva con threading
- Muestra "🤖 Stockfish pensando..."

### Si Stockfish NO Está Instalado
- Selecciona "Stockfish (Motor UCI)" → Muestra aviso
  ```
  ⚠️  Stockfish no disponible.
     👉 Descarga desde: https://stockfishchess.org/download/
     👉 Coloca en: ./stockfish/
     👉 O ejecuta: python verificar_setup.py
  
  Fallback a IA Aleatoria...
  ```
- Automáticamente cambia a IA Aleatoria
- ¡El juego sigue funcionando!

### IA Aleatoria
- Siempre disponible
- Elige movimientos legales al azar
- Rápida (delay de 200ms para visualizar)
- No requiere dependencias externas

---

## 🧪 Testing

```python
# Test 1: Verificar menú funciona
python main.py
# → Seleccionar "Jugador vs Máquina"
# → Debe mostrar submenu con opciones

# Test 2: Stockfish disponible
# → Seleccionar "Stockfish (Motor UCI)"
# → Debe iniciar juego contra Stockfish
# → Ver "🤖 Stockfish pensando..."

# Test 3: Stockfish no disponible
# → Renombrar ./stockfish/stockfish.exe temporalmente
# → Seleccionar "Stockfish (Motor UCI)"
# → Debe mostrar aviso y cambiar a IA Aleatoria automáticamente
# → El juego sigue funcionando

# Test 4: IA Aleatoria
# → Seleccionar "IA Aleatoria"
# → Debe mostrar "🎲 IA Aleatoria pensando..."
# → IA juega movimientos aleatorios validos
```

---

## ✅ Checklist

- [x] Agregar submenu para elegir tipo de IA
- [x] Implementar soporte para Stockfish
- [x] Implementar soporte para IA Aleatoria
- [x] Mostrar mensajes de error claros
- [x] Fallback automático si Stockfish no disponible
- [x] Compilación sin errores
- [x] Verificación de sintaxis

---

## 📋 Archivo Modificado

**`main.py`**
- Menú principal: actualizado
- Función `juego_vs_maquina()`: parametrizado
- Nueva función `_obtener_movimiento_aleatorio()`
- Mejor manejo de errores y mensajes

---

## 🎉 Resultado

Ahora el usuario tiene opciones:

✅ **Jugar con Stockfish** (si está instalado)
- Motor profesional UCI
- Análisis profundo
- Threading asincrónico

✅ **Jugar con IA Aleatoria** (siempre disponible)
- Movimientos legales al azar
- Respuesta rápida
- Fallback automático

✅ **Mensajes claros**
- Si Stockfish no está → Explica cómo instalarlo
- Si hay error → Muestra razón
- Fallback automático → El juego nunca se rompe

---

**Actualización completada**: main.py ahora es más robusto y flexible.
