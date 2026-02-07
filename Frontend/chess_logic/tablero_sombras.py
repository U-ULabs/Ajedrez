"""Tablero del modo Sombras con niebla de guerra."""

from .constantes import *
from .pieza_sombras import (
    PiezaSombraPeon, PiezaSombraCaballo, PiezaSombraAlpil,
    PiezaSombraTorre, PiezaSombraReina, PiezaSombraRey
)


class TableroSombras:
    """Tablero 8x8 con sistema de niebla de guerra y combate RPG."""
    
    def __init__(self, gestor_recursos=None):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piezas = []  # Lista simple en lugar de Sprite Group
        self.niebla = [[True for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.gestor_recursos = gestor_recursos
        self.configurar_tablero()
        self.actualizar_niebla(TEAM_PLAYER)
    
    def configurar_tablero(self):
        """Configura el tablero con disposición estándar de ajedrez."""
        # Blancas (Jugador) - Fila 7 y 6
        self.agregar_pieza(PiezaSombraTorre(0, 7, TEAM_PLAYER, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraCaballo(1, 7, TEAM_PLAYER, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraAlpil(2, 7, TEAM_PLAYER, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraReina(3, 7, TEAM_PLAYER, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraRey(4, 7, TEAM_PLAYER, es_boss=False, gestor_recursos=self.gestor_recursos))
        self.agregar_pieza(PiezaSombraAlpil(5, 7, TEAM_PLAYER, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraCaballo(6, 7, TEAM_PLAYER, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraTorre(7, 7, TEAM_PLAYER, self.gestor_recursos))
        for x in range(8):
            self.agregar_pieza(PiezaSombraPeon(x, 6, TEAM_PLAYER, self.gestor_recursos))
        
        # Negras (Enemigo) - Fila 0 y 1, con Boss
        self.agregar_pieza(PiezaSombraTorre(0, 0, TEAM_ENEMY, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraCaballo(1, 0, TEAM_ENEMY, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraAlpil(2, 0, TEAM_ENEMY, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraReina(3, 0, TEAM_ENEMY, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraRey(4, 0, TEAM_ENEMY, es_boss=True, gestor_recursos=self.gestor_recursos))
        self.agregar_pieza(PiezaSombraAlpil(5, 0, TEAM_ENEMY, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraCaballo(6, 0, TEAM_ENEMY, self.gestor_recursos))
        self.agregar_pieza(PiezaSombraTorre(7, 0, TEAM_ENEMY, self.gestor_recursos))
        for x in range(8):
            self.agregar_pieza(PiezaSombraPeon(x, 1, TEAM_ENEMY, self.gestor_recursos))
    
    def agregar_pieza(self, pieza):
        """Agrega una pieza al tablero."""
        if self.grid[pieza.grid_y][pieza.grid_x] is None:
            self.grid[pieza.grid_y][pieza.grid_x] = pieza
            self.piezas.append(pieza)
        else:
            print(f"No se puede añadir pieza en ({pieza.grid_x},{pieza.grid_y}), casilla ocupada.")
    
    def obtener_pieza_en(self, x, y):
        """Obtiene la pieza en coordenadas (x, y), o None."""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.grid[y][x]
        return None
    
    def mover_pieza(self, pieza, x, y):
        """Mueve una pieza a (x, y), resolviendo combate si es necesario."""
        x_anterior, y_anterior = pieza.grid_x, pieza.grid_y
        
        # Verificar si hay objetivo (captura/ataque)
        objetivo = self.obtener_pieza_en(x, y)
        if objetivo:
            if objetivo.team != pieza.team:
                # Combate RPG
                murio = objetivo.recibir_damage(pieza.damage)
                if murio:
                    if objetivo in self.piezas:
                        self.piezas.remove(objetivo)
                    self.grid[y][x] = None
                    # Si muere, el atacante ocupa la casilla
                    self.grid[y_anterior][x_anterior] = None
                    pieza.grid_x = x
                    pieza.grid_y = y
                    self.grid[y][x] = pieza
                    # pieza.actualizar_posicion_pixel()  <-- Eliminado
                    pieza.post_move(x_anterior, y_anterior, self)
                    
                    if pieza.team == TEAM_PLAYER:
                        self.actualizar_niebla(TEAM_PLAYER)
                    return True
                else:
                    # Ataque sin movimiento (golpeó pero no mató)
                    self.actualizar_niebla(TEAM_PLAYER)
                    return True
        
        # Movimiento normal (casilla vacía)
        if self.obtener_pieza_en(x, y) is None:
            self.grid[y_anterior][x_anterior] = None
            pieza.grid_x = x
            pieza.grid_y = y
            self.grid[y][x] = pieza
            # pieza.actualizar_posicion_pixel() <-- Eliminado
            pieza.post_move(x_anterior, y_anterior, self)
            
            if pieza.team == TEAM_PLAYER:
                self.actualizar_niebla(TEAM_PLAYER)
                
            return True
        
        return False
    
    def actualizar_niebla(self, equipo):
        """Actualiza la niebla de guerra."""
        if equipo != TEAM_PLAYER:
            self.niebla = [[True for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for pieza in self.piezas:
            if pieza.team == equipo:
                # Revelar 3x3 alrededor de la pieza
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = pieza.grid_x + dx, pieza.grid_y + dy
                        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                            self.niebla[ny][nx] = False
    
    def es_visible(self, x, y, equipo):
        """Comprueba si una casilla es visible para el equipo."""
        # Nota: En backend quizás no queramos recalcular niebla cada vez, 
        # pero mantenemos la lógica por ahora.
        self.actualizar_niebla(equipo)
        return not self.niebla[y][x]

    def obtener_piezas_por_equipo(self, equipo):
        """Obtiene todas las piezas de un equipo."""
        return [p for p in self.piezas if p.team == equipo]
    
    def boss_muerto(self):
        """Comprueba si el Boss (Rey enemigo) está muerto."""
        for pieza in self.piezas:
            if pieza.team == TEAM_ENEMY and pieza.es_boss:
                return False
        return True
    
    def jugador_muerto(self):
        """Comprueba si el Rey del jugador está muerto."""
        for pieza in self.piezas:
            if pieza.team == TEAM_PLAYER and pieza.tipo == "REY":
                return False
        return True

    def promocionar_peon(self, peon):
        """Promociona un peón a Reina."""
        x, y = peon.grid_x, peon.grid_y
        team = peon.team
        
        # Eliminar peón
        if peon in self.piezas:
            self.piezas.remove(peon)
        self.grid[y][x] = None
        
        # Crear Reina
        from .pieza_sombras import PiezaSombraReina
        nueva_reina = PiezaSombraReina(x, y, team, self.gestor_recursos)
        
        # Agregar al tablero
        self.agregar_pieza(nueva_reina)
        print(f"¡Promoción! Peón en ({x}, {y}) ahora es una {nueva_reina.nombre}.")
    
    def to_dict(self):
        """Serializa el estado completo del tablero."""
        return {
            "width": GRID_WIDTH,
            "height": GRID_HEIGHT,
            "piezas": [p.to_dict() for p in self.piezas],
            "niebla": self.niebla,
            "game_over": self.boss_muerto() or self.jugador_muerto(),
            "winner": "PLAYER" if self.boss_muerto() else ("ENEMY" if self.jugador_muerto() else None)
        }
