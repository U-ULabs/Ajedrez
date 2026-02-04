"""IA del Boss - Enemigo inteligente con sistema de evaluación tipo Árbol de Decisiones (Minimax) y Poda Alfa-Beta."""

import random
import copy
from .constantes import *
from .pieza_sombras import PiezaSombraPeon


class IASombras:
    """Inteligencia Artificial del Boss con sistema Minimax y Poda Alfa-Beta."""
    
    # Valores base de las piezas para la evaluación
    VALORES_PIEZAS = {
        "PEON": 10,
        "CABALLO": 30,
        "ALFIL": 30,
        "TORRE": 50,
        "REINA": 90,
        "REY": 900,
        "BOSS": 2000 # El Boss es intocable
    }
    
    def __init__(self, tablero):
        self.tablero = tablero
        self.cache_evaluaciones = {} # Transposition Table
    
    def calcular_movimiento(self):
        """Calcula el mejor movimiento usando Minimax con Poda Alfa-Beta."""
        self.cache_evaluaciones.clear() # Limpiar caché por turno
        
        mejor_movimiento = None
        mejor_puntaje = -float('inf')
        
        # Obtener estado ligero del tablero para simulación
        estado_inicial = self._obtener_representacion_estado()
        
        # Búsqueda inicial (Raíz del Minimax)
        posibles_movimientos = self._obtener_todos_los_movimientos(estado_inicial, TEAM_ENEMY)
        
        # Ordenar movimientos para mejorar la poda alfa-beta (heurística de movimiento matador)
        random.shuffle(posibles_movimientos) 
        
        depth = 3 # Profundidad de búsqueda (3 turnos adelante)
        
        for p_idx, nx, ny in posibles_movimientos:
            # Simular movimiento
            nuevo_estado = self._simular_movimiento(estado_inicial, p_idx, nx, ny)
            
            # Llamada recursiva a Minimax
            puntaje = self._minimax(nuevo_estado, depth - 1, -float('inf'), float('inf'), False)
            
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                # Recuperar la pieza real del tablero usando el índice
                pieza_real = self.tablero.obtener_piezas_por_equipo(TEAM_ENEMY)[p_idx]
                mejor_movimiento = (pieza_real, nx, ny)

        return mejor_movimiento

    def _minimax(self, estado, profundidad, alfa, beta, es_maximizando):
        """Algoritmo recursivo Minimax con Poda Alfa-Beta."""
        # Verificar caché
        state_hash = str(estado)
        if state_hash in self.cache_evaluaciones:
            return self.cache_evaluaciones[state_hash]

        # Casos base: profundidad agotada o fin del juego
        if profundidad == 0 or self._esta_terminado(estado):
            ev = self._evaluar_estado(estado)
            self.cache_evaluaciones[state_hash] = ev
            return ev

        if es_maximizando:
            max_eval = -float('inf')
            movimientos = self._obtener_todos_los_movimientos(estado, TEAM_ENEMY)
            for p_idx, nx, ny in movimientos:
                nuevo_estado = self._simular_movimiento(estado, p_idx, nx, ny)
                ev = self._minimax(nuevo_estado, profundidad - 1, alfa, beta, False)
                max_eval = max(max_eval, ev)
                alfa = max(alfa, ev)
                if beta <= alfa:
                    break # Poda
            return max_eval
        else:
            min_eval = float('inf')
            movimientos = self._obtener_todos_los_movimientos(estado, TEAM_PLAYER)
            for p_idx, nx, ny in movimientos:
                nuevo_estado = self._simular_movimiento(estado, p_idx, nx, ny)
                ev = self._minimax(nuevo_estado, profundidad - 1, alfa, beta, True)
                min_eval = min(min_eval, ev)
                beta = min(beta, ev)
                if beta <= alfa:
                    break # Poda
            return min_eval

    def _evaluar_estado(self, estado):
        """Función de evaluación avanzada considerando HP, DMG y posición."""
        puntaje = 0
        piezas = estado['piezas']
        
        for p in piezas:
            valor_base = self.VALORES_PIEZAS.get(p['tipo'], 10)
            
            # Valor ajustado por vida restante (RPG)
            porcentaje_hp = p['hp'] / p['hp_max']
            valor_actual = valor_base * (0.5 + 0.5 * porcentaje_hp)
            
            if p['team'] == TEAM_ENEMY:
                puntaje += valor_actual
                
                # Bonus estratégico: Proteger al Boss
                if p['es_boss']:
                    if porcentaje_hp < 0.3:
                        puntaje -= 500 # Penalización masiva si el Boss está herido
                    
                # Bonus de posición: Control central
                dist_centro = abs(3.5 - p['x']) + abs(3.5 - p['y'])
                puntaje += (8 - dist_centro) * 0.5
            else:
                puntaje -= valor_actual
                
                # Penalización por dejar piezas solas
                # (Bonus si la IA está cerca del Rey jugador)
                if p['tipo'] == "REY":
                    pass # Ya se restó el valor del Rey

        return puntaje

    def _obtener_representacion_estado(self):
        """Convierte las piezas del tablero en una estructura de datos ligera."""
        rep = {'piezas': []}
        for p in self.tablero.piezas:
            rep['piezas'].append({
                'x': p.grid_x,
                'y': p.grid_y,
                'team': p.team,
                'tipo': p.tipo,
                'hp': p.hp,
                'hp_max': p.hp_max,
                'damage': p.damage,
                'es_boss': p.es_boss
            })
        return rep

    def _obtener_todos_los_movimientos(self, estado, equipo):
        """Calcula todos los movimientos posibles para un equipo en un estado dado."""
        movimientos = []
        piezas_equipo = [i for i, p in enumerate(estado['piezas']) if p['team'] == equipo]
        
        # Nota: Aquí usamos una simplificación de los movimientos para no replicar toda la lógica.
        # Pero para que sea preciso, el IASombras debe poder consultar al Tablero real.
        for idx in piezas_equipo:
            p_real = self.tablero.obtener_piezas_por_equipo(equipo)[idx]
            # Usar la lógica real de las clases de piezas
            for nx, ny in p_real.obtener_movimientos_validos(self.tablero):
                movimientos.append((idx, nx, ny))
        return movimientos

    def _simular_movimiento(self, estado, p_idx, nx, ny):
        """Genera un nuevo estado simulando el movimiento."""
        nuevo_estado = copy.deepcopy(estado)
        pieza = nuevo_estado['piezas'][p_idx]
        
        # Verificar si hay captura/ataque
        objetivo = None
        for i, p in enumerate(nuevo_estado['piezas']):
            if p['x'] == nx and p['y'] == ny and i != p_idx:
                objetivo = p
                o_idx = i
                break
        
        if objetivo:
            if objetivo['team'] != pieza['team']:
                # Combate
                objetivo['hp'] -= pieza['damage']
                if objetivo['hp'] <= 0:
                    nuevo_estado['piezas'].pop(o_idx)
                    # Mover a la casilla muerta
                    pieza['x'], pieza['y'] = nx, ny
                # Si no muere, la pieza atacante se queda donde está (mecánica de Sombras)
            else:
                pass # No se debería llegar aquí (movimientos válidos ya filtran aliados)
        else:
            # Movimiento normal
            pieza['x'], pieza['y'] = nx, ny
            
        return nuevo_estado

    def _esta_terminado(self, estado):
        """Verifica si el juego terminó en el estado simulado."""
        has_boss = any(p['es_boss'] for p in estado['piezas'])
        has_king = any(p['team'] == TEAM_PLAYER and p['tipo'] == "REY" for p in estado['piezas'])
        return not has_boss or not has_king

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
                    sombra = PiezaSombraPeon(x, y, TEAM_ENEMY, self.tablero.gestor_recursos)
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
