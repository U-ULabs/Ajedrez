#!/usr/bin/env python3
"""Verificador de Setup - Validar que Stockfish está correctamente instalado.

Uso:
    python verificar_setup.py

Resultado:
    - Verde (✓): Todo OK
    - Amarillo (⚠️): Advertencia no crítica
    - Rojo (✗): Error - Requiere acción
"""

import os
import sys
import subprocess
from pathlib import Path

# Colores para terminal
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_check(mensaje, exitoso=True, advertencia=False):
    """Imprime un mensaje con símbolo de chequeo."""
    if exitoso:
        print(f"{Color.GREEN}✓{Color.END} {mensaje}")
    elif advertencia:
        print(f"{Color.YELLOW}⚠️{Color.END} {mensaje}")
    else:
        print(f"{Color.RED}✗{Color.END} {mensaje}")

def print_header(titulo):
    """Imprime un encabezado."""
    print(f"\n{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BLUE}{titulo:^60}{Color.END}")
    print(f"{Color.BLUE}{'='*60}{Color.END}\n")

def verificar_python():
    """Verifica versión de Python."""
    print_header("1. Python")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version >= (3, 9):
        print_check(f"Python {version_str} (✓ Compatible)")
        return True
    else:
        print_check(f"Python {version_str} (✗ Se requiere 3.9+)", False)
        return False

def verificar_dependencias():
    """Verifica que pygame-ce y python-chess estén instalados."""
    print_header("2. Dependencias Python")
    
    todas_ok = True
    
    # pygame-ce
    try:
        import pygame
        print_check(f"pygame-ce {pygame.__version__} instalado")
    except ImportError:
        print_check("pygame-ce no encontrado", False)
        print("  → Ejecuta: pip install -r requirements.txt")
        todas_ok = False
    
    # python-chess
    try:
        import chess
        print_check(f"python-chess {chess.__version__} instalado")
    except ImportError:
        print_check("python-chess no encontrado", False)
        print("  → Ejecuta: pip install -r requirements.txt")
        todas_ok = False
    
    return todas_ok

def verificar_estructura():
    """Verifica estructura de carpetas del proyecto."""
    print_header("3. Estructura del Proyecto")
    
    raiz = Path(__file__).parent
    archivos_criticos = [
        "main.py",
        "motor_ajedrez.py",
        "modelos.py",
        "reglas.py",
        "ui.py",
        "requirements.txt",
    ]
    
    todas_ok = True
    for archivo in archivos_criticos:
        ruta = raiz / archivo
        if ruta.exists():
            print_check(f"{archivo} presente")
        else:
            print_check(f"{archivo} NO encontrado", False)
            todas_ok = False
    
    return todas_ok

def verificar_stockfish():
    """Verifica que Stockfish esté instalado y funcione."""
    print_header("4. Stockfish")
    
    raiz = Path(__file__).parent
    
    # Búsqueda en orden de preferencia
    rutas_candidatas = [
        raiz / "stockfish" / "stockfish.exe",  # Windows
        raiz / "stockfish" / "stockfish",      # Linux/Mac
        raiz / "bin" / "stockfish.exe",
        raiz / "bin" / "stockfish",
        raiz / "engines" / "stockfish.exe",
        raiz / "engines" / "stockfish",
    ]
    
    ruta_encontrada = None
    for ruta in rutas_candidatas:
        if ruta.exists():
            ruta_encontrada = ruta
            break
    
    # También buscar en PATH
    if not ruta_encontrada:
        try:
            resultado = subprocess.run(
                ["stockfish"] if sys.platform != "win32" else ["stockfish.exe"],
                capture_output=True,
                timeout=1
            )
            if resultado.returncode == 0 or "Stockfish" in resultado.stderr.decode():
                print_check(f"Stockfish encontrado en PATH")
                return True
        except Exception:
            pass
    
    if ruta_encontrada:
        print_check(f"Stockfish encontrado en: {ruta_encontrada}")
        
        # Verificar que se puede ejecutar
        try:
            resultado = subprocess.run(
                str(ruta_encontrada),
                input=b"quit\n",
                capture_output=True,
                timeout=2
            )
            if b"Stockfish" in resultado.stderr or b"Stockfish" in resultado.stdout:
                print_check("Stockfish ejecutable y funciona")
                return True
            else:
                print_check("Stockfish encontrado pero no responde correctamente", False, True)
                return False
        except subprocess.TimeoutExpired:
            print_check("Timeout al ejecutar Stockfish", False, True)
            return False
        except Exception as e:
            print_check(f"Error al ejecutar Stockfish: {e}", False)
            return False
    else:
        print_check("Stockfish NO encontrado", False)
        print(f"\n  📥 Descargar desde: https://stockfishchess.org/download/")
        print(f"  📂 Colocar en: {raiz / 'stockfish'}/")
        print(f"  📄 Archivo: {'stockfish.exe' if sys.platform == 'win32' else 'stockfish'}")
        return False

def verificar_motor_ajedrez():
    """Verifica que motor_ajedrez.py funciona."""
    print_header("5. Módulo motor_ajedrez.py")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from motor_ajedrez import MotorAjedrez, NivelDificultad, EstadoMotor
        
        print_check("motor_ajedrez.py importa correctamente")
        
        # Intentar crear instancia
        motor = MotorAjedrez()
        
        if motor.disponible:
            print_check("MotorAjedrez inicializado correctamente")
            print_check(f"Stockfish disponible: SÍ")
            motor.cerrar()
            return True
        else:
            print_check("MotorAjedrez inicializado pero Stockfish no disponible", False, True)
            return False
    
    except ImportError as e:
        print_check(f"No se puede importar motor_ajedrez: {e}", False)
        return False
    except Exception as e:
        print_check(f"Error al verificar motor_ajedrez: {e}", False)
        return False

def resumen_final(resultados):
    """Imprime resumen final."""
    print_header("📊 Resumen")
    
    total = len(resultados)
    ok = sum(1 for r in resultados.values() if r)
    
    for prueba, resultado in resultados.items():
        estado = "✓" if resultado else "✗"
        color = Color.GREEN if resultado else Color.RED
        print(f"  {color}{estado}{Color.END} {prueba}")
    
    print(f"\n{ok}/{total} verificaciones pasadas")
    
    if ok == total:
        print(f"\n{Color.GREEN}¡PERFECTO! Todo está configurado correctamente.{Color.END}")
        print(f"Ejecuta: {Color.BLUE}python main.py{Color.END}\n")
        return True
    elif ok >= total - 1:
        print(f"\n{Color.YELLOW}⚠️  Stockfish debe descargarse manualmente:{Color.END}")
        print(f"  1. Visita: https://stockfishchess.org/download/")
        print(f"  2. Descarga para tu SO")
        print(f"  3. Extrae en: {Path(__file__).parent / 'stockfish'}/")
        print(f"  4. Ejecuta: python main.py\n")
        return True
    else:
        print(f"\n{Color.RED}✗ Hay problemas que corregir antes de continuar.{Color.END}\n")
        return False

def main():
    print(f"\n{Color.BLUE}╔════════════════════════════════════════════════════════╗{Color.END}")
    print(f"{Color.BLUE}║  Verificador de Setup - Ajedrez Stockfish v2.1       ║{Color.END}")
    print(f"{Color.BLUE}╚════════════════════════════════════════════════════════╝{Color.END}")
    
    resultados = {
        "Python": verificar_python(),
        "Dependencias": verificar_dependencias(),
        "Estructura": verificar_estructura(),
        "motor_ajedrez.py": verificar_motor_ajedrez(),
        "Stockfish": verificar_stockfish(),
    }
    
    listo = resumen_final(resultados)
    return 0 if listo else 1

if __name__ == "__main__":
    sys.exit(main())
