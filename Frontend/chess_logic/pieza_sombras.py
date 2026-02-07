"""Piezas del modo Sombras con sistema RPG de salud y daño.

Este módulo define 7 clases de piezas (Peón, Caballo, Alfil, Torre, Reina, Rey, Boss).
Cada pieza:
- Hereda de PiezaSombra (clase base con HP/DMG)
- Tiene movimientos específicos del ajedrez
- Puede recibir daño
- Se serializa para la API

El Boss es un Rey Caído con el atributo es_boss=True y estadísticas especiales.
"""

from .constantes import *


class PiezaSombra:
    """Pieza base con sistema RPG de salud y daño.
    
    Atributos:
        grid_x, grid_y (int): Posición en el tablero 0-7
        team (str): "JUGADOR" o "ENEMIGO"
        tipo (str): Tipo de pieza ("PEON", "CABALLO", etc.)
        hp, hp_max (int): Puntos de vida actuales y máximos
        damage (int): Daño que inflige en combate
        es_boss (bool): True solo para Rey Caído (enemigo final)
    """
    
    def __init__(self, grid_x, grid_y, team, tipo_key, gestor_recursos=None):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.team = team
        self.tipo = tipo_key
        self.es_boss = False  # Atributo por defecto (solo Rey Caído puede ser True)
        # gestor_recursos se ignora en backend, mantenemos la firma por compatibilidad si es necesario
        
        # Obtener estadísticas RPG según tipo de pieza
        stats = STATS.get(tipo_key, STATS["PEON"])
        self.hp_max = stats["hp"]
        self.hp = self.hp_max
        self.damage = stats["dmg"]
        self.nombre = stats["name"]
        
    def to_dict(self):
        """Serializa el estado de la pieza para la API."""
        return {
            "x": self.grid_x,
            "y": self.grid_y,
            "team": self.team,
            "tipo": self.tipo,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "damage": self.damage,
            "es_boss": self.es_boss,
            "nombre": self.nombre
        }

    def recibir_damage(self, cantidad):
        """Reduce HP y retorna True si la pieza muere."""
        self.hp -= cantidad
        print(f"{self.nombre} ({self.team}) recibió {cantidad} de daño. HP: {self.hp}/{self.hp_max}")
        if self.hp <= 0:
            return True  # Murió
        return False
    
    def obtener_movimientos_validos(self, tablero):
        """Obtiene lista de movimientos válidos para esta pieza."""
        return []
    
    def esta_en_tablero(self, x, y):
        """Verifica si una coordenada está dentro del tablero 8x8."""
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
    
    def obtener_movimientos_direccion(self, tablero, dx, dy, max_pasos=8):
        """Obtiene movimientos válidos en una dirección."""
        movimientos = []
        for i in range(1, max_pasos + 1):
            nx, ny = self.grid_x + (dx * i), self.grid_y + (dy * i)
            if not self.esta_en_tablero(nx, ny):
                break  # Fuera del tablero
            
            objetivo = tablero.obtener_pieza_en(nx, ny)
            if objetivo is None:
                movimientos.append((nx, ny))  # Casilla vacía
            else:
                if objetivo.team != self.team:
                    movimientos.append((nx, ny))  # Captura permitida
                break  # Pieza bloquea
        return movimientos
    
    def post_move(self, x_anterior, y_anterior, tablero):
        """Hook llamado después de mover."""
        pass


class PiezaSombraPeon(PiezaSombra):
    """Peón - Movimiento limitado, capturas diagonales."""
    
    def __init__(self, x, y, team, gestor_recursos=None):
        super().__init__(x, y, team, "PEON", gestor_recursos)
        self.primer_movimiento = True
    
    def obtener_movimientos_validos(self, tablero):
        """Calcula movimientos válidos del peón."""
        movimientos = []
        # Dirección: -1 para jugador (arriba en pantalla), +1 para enemigo (abajo)
        # NOTA: En backend, coordinadas (0,0) es esquina superior izquierda.
        # Jugador empieza en filas inferiores (6,7) y va hacia arriba (disminuye Y).
        # Enemigo empieza en filas superiores (0,1) y va hacia abajo (aumenta Y).
        direccion = -1 if self.team == TEAM_PLAYER else 1
        
        # Movimiento frontal: 1 casilla (o 2 en primer movimiento)
        nx, ny = self.grid_x, self.grid_y + direccion
        if self.esta_en_tablero(nx, ny) and tablero.obtener_pieza_en(nx, ny) is None:
            movimientos.append((nx, ny))
            # Doble movimiento inicial
            if self.primer_movimiento:
                nx2, ny2 = self.grid_x, self.grid_y + (direccion * 2)
                if self.esta_en_tablero(nx2, ny2) and tablero.obtener_pieza_en(nx2, ny2) is None:
                    movimientos.append((nx2, ny2))
        
        # Capturas diagonales
        for dx in [-1, 1]:
            nx, ny = self.grid_x + dx, self.grid_y + direccion
            if self.esta_en_tablero(nx, ny):
                objetivo = tablero.obtener_pieza_en(nx, ny)
                if objetivo and objetivo.team != self.team:
                    movimientos.append((nx, ny))
        
        return movimientos
    
    def post_move(self, x_anterior, y_anterior, tablero):
        self.primer_movimiento = False
        
        # Verificar promoción
        # Fila 0 para jugador, Fila 7 para enemigo
        target_rank = 0 if self.team == TEAM_PLAYER else 7
        if self.grid_y == target_rank:
            tablero.promocionar_peon(self)


class PiezaSombraCaballo(PiezaSombra):
    """Caballo - Movimiento en L (2+1 casillas)."""
    
    def __init__(self, x, y, team, gestor_recursos=None):
        super().__init__(x, y, team, "CABALLO", gestor_recursos)
    
    def obtener_movimientos_validos(self, tablero):
        """Calcula 8 posibles movimientos en L."""
        movimientos = []
        offsets = [
            (1, 2), (1, -2), (-1, 2), (-1, -2),   # 2 vertical, 1 horizontal
            (2, 1), (2, -1), (-2, 1), (-2, -1)    # 2 horizontal, 1 vertical
        ]
        for dx, dy in offsets:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if self.esta_en_tablero(nx, ny):
                objetivo = tablero.obtener_pieza_en(nx, ny)
                if objetivo is None or objetivo.team != self.team:
                    movimientos.append((nx, ny))
        return movimientos


class PiezaSombraAlpil(PiezaSombra):
    """Alfil - Movimiento diagonal."""
    
    def __init__(self, x, y, team, gestor_recursos=None):
        super().__init__(x, y, team, "ALFIL", gestor_recursos)
    
    def obtener_movimientos_validos(self, tablero):
        """Calcula movimientos en las 4 diagonales."""
        movimientos = []
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            movimientos.extend(self.obtener_movimientos_direccion(tablero, dx, dy))
        return movimientos


class PiezaSombraTorre(PiezaSombra):
    """Torre - Movimiento horizontal y vertical."""
    
    def __init__(self, x, y, team, gestor_recursos=None):
        super().__init__(x, y, team, "TORRE", gestor_recursos)
    
    def obtener_movimientos_validos(self, tablero):
        """Calcula movimientos en las 4 direcciones cardinales."""
        movimientos = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            movimientos.extend(self.obtener_movimientos_direccion(tablero, dx, dy))
        return movimientos


class PiezaSombraReina(PiezaSombra):
    """Reina - Movimiento horizontal, vertical y diagonal."""
    
    def __init__(self, x, y, team, gestor_recursos=None):
        super().__init__(x, y, team, "REINA", gestor_recursos)
    
    def obtener_movimientos_validos(self, tablero):
        """Calcula movimientos en todas las 8 direcciones."""
        movimientos = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            movimientos.extend(self.obtener_movimientos_direccion(tablero, dx, dy))
        return movimientos


class PiezaSombraRey(PiezaSombra):
    """Rey - Movimiento un paso en cualquier dirección."""
    
    def __init__(self, x, y, team, es_boss=False, gestor_recursos=None):
        # Si es Boss, usa estadísticas especiales ("BOSS" en STATS)
        tipo_key = "BOSS" if es_boss else "REY"
        super().__init__(x, y, team, tipo_key, gestor_recursos)
        self.es_boss = es_boss  # Marca el Rey Caído
    
    def obtener_movimientos_validos(self, tablero):
        """Calcula movimiento limitado a 1 casilla en cualquier dirección."""
        movimientos = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if self.esta_en_tablero(nx, ny):
                objetivo = tablero.obtener_pieza_en(nx, ny)
                if objetivo is None or objetivo.team != self.team:
                    movimientos.append((nx, ny))
        return movimientos
