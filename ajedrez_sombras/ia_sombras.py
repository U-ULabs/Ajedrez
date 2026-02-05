"""IA del Boss - Enemigo inteligente con sistema de evaluación tipo Árbol de Decisiones (Minimax) y Poda Alfa-Beta."""

import random
import copy
import json
import os
from .constantes import *
from .pieza_sombras import PiezaSombraPeon


class VirtualBoard:
    """Clase ligera para simular movimientos sin afectar el tablero real."""
    def __init__(self, piezas_data):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piezas = []
        for p_data in piezas_data:
            p_obj = type('VirtualPiece', (), p_data)
            self.grid[p_data['y']][p_data['x']] = p_obj
            self.piezas.append(p_obj)

    def obtener_pieza_en(self, x, y):
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.grid[y][x]
        return None


class IASombras:
    """Inteligencia Artificial del Boss con sistema Minimax, Poda Alfa-Beta y RL-Lite."""
    
    VALORES_PIEZAS = {
        "PEON": 10,
        "CABALLO": 30,
        "ALFIL": 30,
        "TORRE": 50,
        "REINA": 90,
        "REY": 1000,
        "BOSS": 2000
    }
    
    PESOS_DEFECTO = {
        "W_MATERIAL": 1.0,      # Importancia del valor de las piezas
        "W_BOSS_SAFETY": 1.0,   # Importancia de la vida del Boss
        "W_CENTER": 0.5,        # Importancia de controlar el centro
        "W_AGGRESSION": 1.0     # Tendencia a atacar piezas enemigas
    }
    
    def __init__(self, tablero):
        self.tablero = tablero
        self.cache_evaluaciones = {}
        self.ruta_pesos = os.path.join(os.path.dirname(__file__), "ia_weights.json")
        self.pesos = self._cargar_pesos()
    
    def _cargar_pesos(self):
        """Carga los pesos aprendidos de partidas anteriores."""
        if os.path.exists(self.ruta_pesos):
            try:
                with open(self.ruta_pesos, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar pesos de IA: {e}")
        return self.PESOS_DEFECTO.copy()
    
    def _guardar_pesos(self):
        """Guarda los pesos actuales en el archivo JSON."""
        try:
            with open(self.ruta_pesos, 'w') as f:
                json.dump(self.pesos, f, indent=4)
        except Exception as e:
            print(f"Error al guardar pesos de IA: {e}")

    def aprender_de_resultado(self, gano_ia):
        """Ajusta los pesos basándose en si la IA ganó o perdió."""
        if gano_ia:
            print("IA: 'He ganado. Reforzando táctica actual.'")
            # Reforzar ligeramente la agresividad
            self.pesos["W_AGGRESSION"] = min(2.0, self.pesos["W_AGGRESSION"] + 0.05)
        else:
            print("IA: 'He perdido. Ajustando defensa y seguridad del Boss.'")
            # Aumentar importancia de la seguridad y bajar agresividad suicida
            self.pesos["W_BOSS_SAFETY"] = min(3.0, self.pesos["W_BOSS_SAFETY"] + 0.15)
            self.pesos["W_AGGRESSION"] = max(0.5, self.pesos["W_AGGRESSION"] - 0.1)
            
        self._guardar_pesos()
        print(f"Nuevos pesos de IA: {self.pesos}")
    
    def calcular_movimiento(self):
        self.cache_evaluaciones.clear()
        
        estado_inicial = self._obtener_representacion_estado()
        posibles_movimientos = self._obtener_todos_los_movimientos(estado_inicial, TEAM_ENEMY)
        
        if not posibles_movimientos:
            return None

        # Métrica de predicciones dinámica: 
        # (Movimientos posibles actuales) x 130 (estimación de duración)
        # Esto reemplaza el estático 3x16 (48) x 130 para que fluctúe durante la partida.
        predicciones = self.obtener_predicciones_estimadas(posibles_movimientos)
        print(f"Capacidad de Predicción de IA: {predicciones}")
        
        mejor_movimiento = None
        mejor_puntaje = -float('inf')
        
        random.shuffle(posibles_movimientos) 
        depth = 3
        
        for p_idx_in_estado, nx, ny in posibles_movimientos:
            nuevo_estado = self._simular_movimiento(estado_inicial, p_idx_in_estado, nx, ny)
            puntaje = self._minimax(nuevo_estado, depth - 1, -float('inf'), float('inf'), False)
            
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                # Recuperar la pieza real usando el objeto guardado en p_data
                p_data = estado_inicial['piezas'][p_idx_in_estado]
                mejor_movimiento = (p_data['original_obj'], nx, ny)

        return mejor_movimiento

    def obtener_predicciones_estimadas(self, posibles_movimientos):
        """Calcula la complejidad de predicción de forma dinámica."""
        # Fórmula: Movimientos totales disponibles x 130 (factor de duración sugerido)
        # Dividimos por un factor de escala para que el rango sea más reactivo dentro de 1-1000
        total_movs = len(posibles_movimientos)
        valor = total_movs * 130 / 10
        return max(1, min(1000, int(valor)))

    def _minimax(self, estado, profundidad, alfa, beta, es_maximizando):
        # Crear un hash estable sin incluir las referencias a objetos
        state_hash = tuple(sorted((p['x'], p['y'], p['team'], p['tipo'], p['hp']) for p in estado['piezas']))
        if state_hash in self.cache_evaluaciones:
            return self.cache_evaluaciones[state_hash]

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
                    break
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
                    break
            return min_eval

    def _evaluar_estado(self, estado):
        puntaje = 0
        w_mat = self.pesos.get("W_MATERIAL", 1.0)
        w_boss = self.pesos.get("W_BOSS_SAFETY", 1.0)
        w_center = self.pesos.get("W_CENTER", 0.5)
        w_agg = self.pesos.get("W_AGGRESSION", 1.0)

        for p in estado['piezas']:
            valor_base = self.VALORES_PIEZAS.get(p['tipo'], 10)
            porcentaje_hp = p['hp'] / p['hp_max']
            valor_actual = valor_base * (0.5 + 0.5 * porcentaje_hp)
            
            if p['team'] == TEAM_ENEMY:
                # Bonificación por material propio
                puntaje += valor_actual * w_mat
                
                # Bonus por seguridad del Boss
                if p['es_boss']:
                    # Si el Boss tiene poca vida, es un castigo masivo (ajustado por peso)
                    if porcentaje_hp < 0.3:
                        puntaje -= 1000 * w_boss
                    else:
                        puntaje += 500 * porcentaje_hp * w_boss
                    
                # Control del centro
                dist_centro = abs(3.5 - p['x']) + abs(3.5 - p['y'])
                puntaje += (8 - dist_centro) * w_center
            else:
                # Castigo por material del jugador (agresividad)
                # Si W_AGGRESSION es alto, la IA valora más quitar piezas al jugador
                puntaje -= valor_actual * w_agg
                
        return puntaje

    def _obtener_representacion_estado(self):
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
                'es_boss': p.es_boss,
                'original_obj': p # Guardar referencia al objeto real
            })
        return rep

    def _obtener_todos_los_movimientos(self, estado, equipo):
        movimientos = []
        v_board = VirtualBoard(estado['piezas'])
        
        for idx, p_data in enumerate(estado['piezas']):
            if p_data['team'] == equipo:
                p_real = p_data['original_obj']
                
                old_x, old_y = p_real.grid_x, p_real.grid_y
                p_real.grid_x, p_real.grid_y = p_data['x'], p_data['y']
                
                validos = p_real.obtener_movimientos_validos(v_board)
                
                p_real.grid_x, p_real.grid_y = old_x, old_y
                
                for nx, ny in validos:
                    movimientos.append((idx, nx, ny))
        return movimientos

    def _simular_movimiento(self, estado, p_idx, nx, ny):
        # Usar copy.copy y manejar la lista de piezas manualmente para evitar deepcopy de objetos pieza
        nuevo_estado = {
            'piezas': [p.copy() for p in estado['piezas']]
        }
        pieza = nuevo_estado['piezas'][p_idx]
        
        o_idx = -1
        for i, p in enumerate(nuevo_estado['piezas']):
            if p['x'] == nx and p['y'] == ny and i != p_idx:
                o_idx = i
                break
        
        if o_idx != -1:
            objetivo = nuevo_estado['piezas'][o_idx]
            if objetivo['team'] != pieza['team']:
                objetivo['hp'] -= pieza['damage']
                if objetivo['hp'] <= 0:
                    nuevo_estado['piezas'].pop(o_idx)
                    # Si la pieza que se movió estaba después en la lista, su índice cambió
                    if o_idx < p_idx:
                        # Buscamos la pieza de nuevo por referencia si fuera necesario, 
                        # pero aquí simplemente actualizamos la posición de la pieza correcta.
                        pieza['x'], pieza['y'] = nx, ny
                    else:
                        pieza['x'], pieza['y'] = nx, ny
        else:
            pieza['x'], pieza['y'] = nx, ny
            
        return nuevo_estado

    def _esta_terminado(self, estado):
        has_boss = any(p['es_boss'] for p in estado['piezas'])
        has_king = any(p['team'] == TEAM_PLAYER and p['tipo'] == "REY" for p in estado['piezas'])
        return not has_boss or not has_king

    def invocar_sombra(self):
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
        for pieza in self.tablero.piezas:
            if pieza.team == TEAM_ENEMY and pieza.es_boss:
                return pieza
        return None
    
    def _obtener_rey_jugador(self):
        for pieza in self.tablero.piezas:
            if pieza.team == TEAM_PLAYER and pieza.tipo == "REY":
                return pieza
        return None
