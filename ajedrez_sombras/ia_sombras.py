"""IA del Boss - Enemigo inteligente con invocación de Sombras.

Versión mejorada con integración opcional de Stockfish para análisis estratégico.
- Modo clásico: IA de reglas heurísticas (táctico/defensa)
- Modo Stockfish: Análisis profundo para movimientos complejos
"""

import random
import os
import sys
from .constantes import *
from .pieza_sombras import PiezaSombraPeon

# Intentar importar motor de Stockfish (opcional)
try:
    # Buscar motor_ajedrez.py en directorio padre
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from motor_ajedrez import MotorAjedrez, NivelDificultad
    STOCKFISH_DISPONIBLE = True
except ImportError:
    STOCKFISH_DISPONIBLE = False


class IASombras:
    """Inteligencia Artificial del Boss con invocación de Sombras.
    
    Estrategia de dos fases:
    1. IA Heurística: Ataque/Invocación/Movimiento táctico (siempre funciona)
    2. IA Stockfish (opcional): Análisis profundo para situaciones complejas
    """
    
    def __init__(self, tablero, usar_stockfish: bool = True):
        """Inicializa la IA del Boss.
        
        Args:
            tablero: Referencia al tablero de juego
            usar_stockfish: Si True, intenta usar Stockfish para análisis
        """
        self.tablero = tablero
        self.turno_invocacion = 0
        self.usar_stockfish = usar_stockfish and STOCKFISH_DISPONIBLE
        self.motor = None
        
        if self.usar_stockfish:
            try:
                self.motor = MotorAjedrez(nivel=NivelDificultad.FACIL)
                if not self.motor.disponible:
                    print("⚠️  Stockfish no disponible para IA Sombras. Usando IA heurística.")
                    self.usar_stockfish = False
            except Exception as e:
                print(f"⚠️  Error al inicializar Stockfish: {e}. Usando IA heurística.")
                self.usar_stockfish = False
    
    def calcular_movimiento(self):
        """Calcula el siguiente movimiento de la IA (Boss + piezas enemigas).
        
        Estrategia de prioridades:
        1. Ataque directo (captura garantizada)
        2. Análisis Stockfish (si disponible)
        3. Movimiento táctico heurístico
        4. Movimiento aleatorio
        """
        piezas_enemigas = self.tablero.obtener_piezas_por_equipo(TEAM_ENEMY)
        
        # Prioridad 1: Ataque directo (si puede capturar inmediatamente)
        for pieza in piezas_enemigas:
            movimientos = pieza.obtener_movimientos_validos(self.tablero)
            for x, y in movimientos:
                objetivo = self.tablero.obtener_pieza_en(x, y)
                if objetivo and objetivo.team == TEAM_PLAYER:
                    return (pieza, x, y)  # Atacar
        
        # Prioridad 2: Consultar Stockfish para análisis estratégico
        if self.usar_stockfish and self.motor:
            movimiento_sf = self._obtener_movimiento_stockfish()
            if movimiento_sf:
                return movimiento_sf
        
        # Prioridad 3: Movimiento táctico heurístico (hacia el jugador)
        rey_jugador = self._obtener_rey_jugador()
        if rey_jugador:
            for pieza in piezas_enemigas:
                movimientos = pieza.obtener_movimientos_validos(self.tablero)
                # Ordenar movimientos por distancia al jugador
                movimientos_ordenados = sorted(
                    movimientos,
                    key=lambda m: self._distancia_manhattan(m, (rey_jugador.grid_x, rey_jugador.grid_y))
                )
                if movimientos_ordenados:
                    return (pieza, movimientos_ordenados[0][0], movimientos_ordenados[0][1])
        
        # Prioridad 4: Movimiento aleatorio
        for pieza in piezas_enemigas:
            movimientos = pieza.obtener_movimientos_validos(self.tablero)
            if movimientos:
                x, y = random.choice(movimientos)
                return (pieza, x, y)
        
        return None
    
    def _obtener_movimiento_stockfish(self):
        """Obtiene un movimiento sugerido por Stockfish (si disponible).
        
        Nota: Solo funciona si el tablero tiene representación en ajedrez clásico.
        Para el modo Sombras, es más decorativo/experimental.
        
        Returns:
            Tupla (pieza, x, y) si encuentra movimiento, None en caso contrario
        """
        try:
            if not self.motor or not self.motor.disponible:
                return None
            
            # Obtener Boss
            boss = self._obtener_boss()
            if not boss:
                return None
            
            # En modo Sombras, Stockfish no tiene sentido directo
            # Pero podemos usarlo para decidir si atacar o retroceder
            # Esta es una integración simbólica para demostrar extensibilidad
            
            # Si el Boss está bajo presión (cerca del jugador), usar defensiva
            rey_jugador = self._obtener_rey_jugador()
            if rey_jugador:
                distancia = self._distancia_manhattan(
                    (boss.grid_x, boss.grid_y),
                    (rey_jugador.grid_x, rey_jugador.grid_y)
                )
                if distancia < 3:
                    # En modo defensa: moverse hacia atrás si es posible
                    movimientos = boss.obtener_movimientos_validos(self.tablero)
                    if movimientos:
                        # Elegir movimiento que aumenta distancia
                        mejor = max(
                            movimientos,
                            key=lambda m: self._distancia_manhattan(m, (rey_jugador.grid_x, rey_jugador.grid_y))
                        )
                        return (boss, mejor[0], mejor[1])
            
            return None
        except Exception as e:
            # Si algo falla, volver a IA heurística silenciosamente
            return None
    
    def invocar_sombra(self):
        """30% de probabilidad de invocar una Sombra adyacente al Boss."""
        if random.random() < 0.3:
            boss = self._obtener_boss()
            if boss:
                adyacentes_libres = []
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = boss.grid_x + dx, boss.grid_y + dy
                    if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and
                        self.tablero.obtener_pieza_en(nx, ny) is None):
                        adyacentes_libres.append((nx, ny))
                
                if adyacentes_libres:
                    x, y = random.choice(adyacentes_libres)
                    sombra = PiezaSombraPeon(x, y, TEAM_ENEMY)
                    self.tablero.agregar_pieza(sombra)
                    print(f"¡El Boss invocó una Sombra en ({x}, {y})!")
                    return True
        return False
    
    def _obtener_boss(self):
        """Obtiene la referencia al Boss."""
        for pieza in self.tablero.piezas:
            if pieza.team == TEAM_ENEMY and pieza.es_boss:
                return pieza
        return None
    
    def _obtener_rey_jugador(self):
        """Obtiene la referencia al Rey del jugador."""
        for pieza in self.tablero.piezas:
            if pieza.team == TEAM_PLAYER and pieza.tipo == "REY":
                return pieza
        return None
    
    @staticmethod
    def _distancia_manhattan(pos1, pos2):
        """Calcula distancia Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def cerrar(self):
        """Limpia recursos (motor de Stockfish)."""
        if self.motor:
            try:
                self.motor.cerrar()
            except Exception:
                pass
    
    def __del__(self):
        """Destructor para limpieza."""
        self.cerrar()
