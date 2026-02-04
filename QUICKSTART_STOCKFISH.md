# ⚡ Guía de Inicio Rápido - Stockfish v2.1

## 🚀 En 5 Minutos

### 1. Descargar Stockfish
👉 **https://stockfishchess.org/download/**
- Selecciona tu SO (Windows/Linux/Mac)
- Descarga el ZIP más reciente

### 2. Crear carpeta
```powershell
# Windows
mkdir e:\GIT\Ajedrez\stockfish
```

### 3. Extraer binario
```
Descomprime el ZIP
Copia stockfish.exe (Windows) o stockfish (Linux/Mac)
Pega en: e:\GIT\Ajedrez\stockfish\
```

### 4. ¡Listo!
```powershell
python main.py
→ AJEDREZ CLÁSICO
→ Jugador vs Máquina (Stockfish) ✓
```

---

## 🎮 Usar el Juego

| Acción | Resultado |
|--------|----------|
| Click pieza blanca | Seleccionar/mover |
| Esperar turno negro | Stockfish piensa (UI activa) |
| Jugar hasta fin | Juego termina |

---

## ⚙️ Configurar Dificultad

**Archivo:** `main.py`  
**Línea:** ~145

```python
# Cambiar MEDIO a:
motor = MotorAjedrez(nivel=NivelDificultad.FACIL)      # Fácil
motor = MotorAjedrez(nivel=NivelDificultad.DIFICIL)    # Difícil
motor = MotorAjedrez(nivel=NivelDificultad.ANALISIS)   # Muy fuerte
```

---

## ✅ Verificar Funcionamiento

```python
# En Python REPL o script
from motor_ajedrez import MotorAjedrez

motor = MotorAjedrez()
print("✓ Stockfish OK" if motor.disponible else "✗ No encontrado")
motor.cerrar()
```

---

## 🆘 Problema: "Stockfish no encontrado"

**Solución:**
1. ¿Descargaste el ZIP desde https://stockfishchess.org/download/?
2. ¿Lo extrajiste en `e:\GIT\Ajedrez\stockfish\`?
3. ¿Está el archivo `stockfish.exe` (Windows) en esa carpeta?

Si todo OK pero sigue errando → Lee [docs/STOCKFISH.md](docs/STOCKFISH.md)

---

## 📖 Documentación

- **Instalación detallada:** [docs/STOCKFISH.md](docs/STOCKFISH.md)
- **Cambios técnicos:** [CAMBIOS_v2.1_STOCKFISH.md](CAMBIOS_v2.1_STOCKFISH.md)
- **Resumen completo:** [RESUMEN_IMPLEMENTACION_STOCKFISH.md](RESUMEN_IMPLEMENTACION_STOCKFISH.md)

---

**¡Disfruta jugando contra Stockfish!** 🎉
