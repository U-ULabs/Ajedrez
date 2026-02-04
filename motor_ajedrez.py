"""Motor de Ajedrez - Integración centralizada con Stockfish.

Proporciona una interfaz unificada para usar Stockfish en todos los modos:
- Ajedrez Clásico vs Máquina
- Ajedrez Sombras (IA del Boss)
- Análisis y sugerencias de movimientos

Características:
- Detección automática de Stockfish (PATH, ./bin, ./stockfish/)
- Niveles de dificultad configurable (fácil/medio/difícil/análisis)
- Operación no-bloqueante con threading
- Manejo robusto de errores y fallback
- Compatible con python-chess UCI
"""

import os
import sys
import subprocess
import threading
import shutil
from typing import Optional, Tuple, Dict, Callable
from enum import Enum

try:
    import chess
    import chess.engine
except ImportError:
    chess = None
    chess_engine = None

from modelos import Color, TipoPieza
from ajedrez_clasico import Pieza


class NivelDificultad(Enum):
    """Niveles de dificultad del motor."""
    FACIL = 100          # 100ms por movimiento
    MEDIO = 500          # 500ms por movimiento
    DIFICIL = 2000       # 2s por movimiento
    ANALISIS = 5000      # 5s para análisis profundo
    
    def a_milisegundos(self) -> int:
        return self.value


class EstadoMotor(Enum):
    """Estados de ejecución del motor."""
    INACTIVO = "inactivo"
    CALCULANDO = "calculando"
    LISTO = "listo"
    ERROR = "error"


class ResultadoMotor:
    """Encapsula el resultado de una búsqueda del motor."""
    
    def __init__(self, movimiento_lan: Optional[str] = None, 
                 evaluacion: Optional[float] = None,
                 profundidad: int = 0,
                 error: Optional[str] = None):
        self.movimiento_lan = movimiento_lan  # En formato e2e4
        self.evaluacion = evaluacion          # Ventaja en centipeones
        self.profundidad = profundidad        # Profundidad analizada
        self.error = error                    # Mensaje de error si aplica
    
    @property
    def exitoso(self) -> bool:
        return self.movimiento_lan is not None and self.error is None


class MotorAjedrez:
    """Interfaz centralizada para el motor Stockfish UCI.
    
    Maneja:
    - Detección y validación del binario
    - Búsqueda no-bloqueante de movimientos
    - Configuración de niveles de dificultad
    - Conversión automática entre FEN y tablero interno
    """
    
    def __init__(self, ruta_motor: Optional[str] = None, 
                 nivel: NivelDificultad = NivelDificultad.MEDIO):
        """Inicializa el motor.
        
        Args:
            ruta_motor: Ruta al binario de Stockfish. Si es None, detecta automáticamente.
            nivel: Nivel de dificultad (tiempo de reflexión).
        """
        self.ruta_motor = ruta_motor or self._detectar_stockfish()
        self.nivel = nivel
        self.engine = None
        self.disponible = False
        self.estado = EstadoMotor.INACTIVO
        
        # Threading para búsqueda no-bloqueante
        self.hilo_busqueda = None
        self.resultado_actual = None
        self.callback_resultado = None
        self._lock = threading.Lock()
        
        self._inicializar()
    
    def _detectar_stockfish(self) -> Optional[str]:
        """Resuelve la ruta del binario de Stockfish.
        
        Busca en este orden:
        1. PATH del sistema
        2. ./bin/stockfish
        3. ./engines/stockfish
        4. ./stockfish/stockfish
        5. Variantes en carpeta ./stockfish/
        
        Returns:
            Ruta al ejecutable o None si no está disponible.
        """
        exe_name = "stockfish.exe" if sys.platform.startswith("win") else "stockfish"
        
        # 1) Buscar en PATH
        ruta = shutil.which(exe_name)
        if ruta:
            return ruta
        
        # 2) Buscar localmente
        raiz = os.path.dirname(os.path.abspath(__file__))
        candidatos = [
            os.path.join(raiz, exe_name),
            os.path.join(raiz, "bin", exe_name),
            os.path.join(raiz, "engines", exe_name),
            os.path.join(raiz, "stockfish", exe_name),
        ]
        
        for c in candidatos:
            if os.path.isfile(c):
                return os.path.abspath(c)
        
        # 3) Buscar variantes en /stockfish
        carpeta_stockfish = os.path.join(raiz, "stockfish")
        if os.path.isdir(carpeta_stockfish):
            try:
                for nombre in os.listdir(carpeta_stockfish):
                    if nombre.lower().startswith("stockfish"):
                        ruta_candidata = os.path.join(carpeta_stockfish, nombre)
                        if os.path.isfile(ruta_candidata):
                            return os.path.abspath(ruta_candidata)
            except Exception:
                pass
        
        return None
    
    def _inicializar(self) -> bool:
        """Inicializa la conexión con el motor UCI.
        
        Returns:
            True si se conectó exitosamente, False en caso contrario.
        """
        if not self.ruta_motor:
            self.disponible = False
            self.estado = EstadoMotor.ERROR
            print("❌ Stockfish no encontrado. Ver instrucciones en docs/STOCKFISH.md")
            return False
        
        if not os.path.isfile(self.ruta_motor):
            self.disponible = False
            self.estado = EstadoMotor.ERROR
            print(f"❌ El archivo {self.ruta_motor} no existe")
            return False
        
        try:
            # Intentar conectar con el motor
            self.engine = chess.engine.SimpleEngine.popen_uci(self.ruta_motor)
            self.disponible = True
            self.estado = EstadoMotor.INACTIVO
            print(f"✓ Stockfish conectado: {self.ruta_motor}")
            return True
        except Exception as e:
            self.disponible = False
            self.estado = EstadoMotor.ERROR
            print(f"❌ Error al conectar Stockfish: {e}")
            return False
    
    def buscar_movimiento(self, tablero_casillas: Dict[Tuple[int, int], Optional[Pieza]], 
                         turno: Color, callback: Optional[Callable] = None) -> Optional[str]:
        """Busca el mejor movimiento de forma bloqueante.
        
        Args:
            tablero_casillas: Diccionario de casillas del tablero
            turno: Color del jugador actual
            callback: Función opcional llamada cuando está listo
        
        Returns:
            Movimiento en formato LAN (e2e4) o None si hay error
        """
        if not self.disponible:
            return None
        
        try:
            self.estado = EstadoMotor.CALCULANDO
            fen = self._tablero_a_fen(tablero_casillas, turno)
            board = chess.Board(fen)
            
            # Buscar movimiento con límite de tiempo
            limit = chess.engine.Limit(time=self.nivel.a_milisegundos() / 1000.0)
            info = self.engine.play(board, limit, info=chess.engine.INFO_ALL)
            
            if info.move:
                resultado = ResultadoMotor(
                    movimiento_lan=info.move.uci(),
                    evaluacion=float(info.info.get("score", 0)) if "score" in info.info else None,
                    profundidad=info.info.get("depth", 0)
                )
                self.estado = EstadoMotor.LISTO
                if callback:
                    callback(resultado)
                return resultado.movimiento_lan
            else:
                self.estado = EstadoMotor.ERROR
                return None
        except Exception as e:
            self.estado = EstadoMotor.ERROR
            print(f"Error en búsqueda del motor: {e}")
            return None
    
    def buscar_movimiento_async(self, tablero_casillas: Dict[Tuple[int, int], Optional[Pieza]], 
                                turno: Color, callback: Callable) -> bool:
        """Busca el mejor movimiento de forma asincrónica en un hilo.
        
        Args:
            tablero_casillas: Diccionario de casillas del tablero
            turno: Color del jugador actual
            callback: Función llamada con ResultadoMotor cuando está listo
        
        Returns:
            True si se inició la búsqueda, False si hay error
        """
        if not self.disponible or self.estado == EstadoMotor.CALCULANDO:
            return False
        
        # Si hay un hilo anterior, esperar a que termine
        if self.hilo_busqueda and self.hilo_busqueda.is_alive():
            return False
        
        self.callback_resultado = callback
        self.hilo_busqueda = threading.Thread(
            target=self._busqueda_en_hilo,
            args=(tablero_casillas, turno, callback),
            daemon=True
        )
        self.hilo_busqueda.start()
        return True
    
    def _busqueda_en_hilo(self, tablero_casillas: Dict[Tuple[int, int], Optional[Pieza]], 
                         turno: Color, callback: Callable):
        """Ejecuta la búsqueda en un hilo separado."""
        try:
            self.estado = EstadoMotor.CALCULANDO
            fen = self._tablero_a_fen(tablero_casillas, turno)
            board = chess.Board(fen)
            
            limit = chess.engine.Limit(time=self.nivel.a_milisegundos() / 1000.0)
            info = self.engine.play(board, limit, info=chess.engine.INFO_ALL)
            
            if info.move:
                resultado = ResultadoMotor(
                    movimiento_lan=info.move.uci(),
                    evaluacion=float(info.info.get("score", 0)) if "score" in info.info else None,
                    profundidad=info.info.get("depth", 0)
                )
            else:
                resultado = ResultadoMotor(error="No se encontró movimiento legal")
            
            self.estado = EstadoMotor.LISTO
        except Exception as e:
            resultado = ResultadoMotor(error=str(e))
            self.estado = EstadoMotor.ERROR
        
        with self._lock:
            self.resultado_actual = resultado
        
        if callback:
            callback(resultado)
    
    def obtener_resultado_actual(self) -> Optional[ResultadoMotor]:
        """Obtiene el resultado actual de forma thread-safe."""
        with self._lock:
            return self.resultado_actual
    
    def esta_calculando(self) -> bool:
        """Retorna True si el motor está en búsqueda."""
        return self.estado == EstadoMotor.CALCULANDO
    
    def establecer_nivel(self, nivel: NivelDificultad):
        """Cambia el nivel de dificultad."""
        self.nivel = nivel
    
    def _tablero_a_fen(self, casillas: Dict[Tuple[int, int], Optional[Pieza]], 
                      turno: Color) -> str:
        """Convierte el tablero interno a FEN estándar."""
        filas = []
        for y in range(7, -1, -1):  # de fila 7 a 0
            vacias = 0
            fila_fen = ""
            for x in range(8):
                p = casillas.get((x, y))
                if not p:
                    vacias += 1
                else:
                    if vacias > 0:
                        fila_fen += str(vacias)
                        vacias = 0
                    tipo = p.tipo
                    mapa = {
                        TipoPieza.PEON: "p",
                        TipoPieza.TORRE: "r",
                        TipoPieza.CABALLO: "n",
                        TipoPieza.ALFIL: "b",
                        TipoPieza.REINA: "q",
                        TipoPieza.REY: "k",
                    }
                    letra = mapa.get(tipo, "p")
                    if p.color == Color.BLANCO:
                        letra = letra.upper()
                    fila_fen += letra
            if vacias > 0:
                fila_fen += str(vacias)
            filas.append(fila_fen)
        fen_pos = "/".join(filas)
        turno_char = "w" if turno == Color.BLANCO else "b"
        return f"{fen_pos} {turno_char} - - 0 1"
    
    def cerrar(self):
        """Cierra la conexión con el motor."""
        if self.hilo_busqueda and self.hilo_busqueda.is_alive():
            # Esperar a que termine el hilo de búsqueda
            self.hilo_busqueda.join(timeout=1.0)
        
        if self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass
        
        self.disponible = False
        self.estado = EstadoMotor.INACTIVO
        print("Motor cerrado")
    
    def __del__(self):
        """Limpieza al destruir la instancia."""
        self.cerrar()
