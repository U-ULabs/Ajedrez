from .tablero_sombras import TableroSombras
from .ia_sombras import IASombras
from .constantes import TEAM_PLAYER, TEAM_ENEMY

class GameManager:
    def __init__(self):
        self.tablero = TableroSombras()
        self.ia = IASombras(self.tablero)
        self.turno = TEAM_PLAYER
        self.game_over = False
        self.winner = None
        self.logs = []

    def reset_game(self):
        self.tablero = TableroSombras()
        self.ia = IASombras(self.tablero)
        self.turno = TEAM_PLAYER
        self.game_over = False
        self.winner = None
        self.logs = ["Partida iniciada"]

    def get_game_state(self):
        state = self.tablero.to_dict()
        state["turno"] = self.turno
        state["logs"] = self.logs[-5:] # Últimos 5 logs
        return state

    def move_player(self, from_x, from_y, to_x, to_y):
        if self.game_over:
            return {"success": False, "message": "Juego terminado"}
        
        if self.turno != TEAM_PLAYER:
            return {"success": False, "message": "No es tu turno"}

        pieza = self.tablero.obtener_pieza_en(from_x, from_y)
        if not pieza or pieza.team != TEAM_PLAYER:
            return {"success": False, "message": "No hay pieza tuya en origen"}

        movimientos = pieza.obtener_movimientos_validos(self.tablero)
        if (to_x, to_y) not in movimientos:
            return {"success": False, "message": "Movimiento inválido"}

        # Ejecutar movimiento
        self.tablero.mover_pieza(pieza, to_x, to_y)
        self.logs.append(f"Jugador movió {pieza.nombre} a ({to_x}, {to_y})")
        
        # Verificar victoria/derrota
        self._check_game_over()
        
        if not self.game_over:
            self.turno = TEAM_ENEMY
            # Trigger AI turn immediately or wait for separate call?
            # For simplicity, trigger logic here or require frontend to request AI move?
            # Let's handle AI move here for synchronous experience, or separate/async?
            # Web requests are usually request/response. 
            # If AI takes time, user waits. IA seems fast enough (depth 3).
            self.move_ai()
        
        return {"success": True, "state": self.get_game_state()}

    def move_ai(self):
        if self.game_over:
            return

        self.ia.invocar_sombra()
        movimiento = self.ia.calcular_movimiento()
        
        if movimiento:
            pieza, x, y = movimiento
            self.tablero.mover_pieza(pieza, x, y)
            self.logs.append(f"IA movió {pieza.nombre} a ({x}, {y})")
        else:
            self.logs.append("IA no tiene movimientos válidos")

        self._check_game_over()
        if not self.game_over:
            self.turno = TEAM_PLAYER

    def _check_game_over(self):
        if self.tablero.boss_muerto():
            self.game_over = True
            self.winner = "PLAYER"
            self.logs.append("¡VICTORIA! Has derrotado al Rey Caído")
            self.ia.aprender_de_resultado(gano_ia=False)
        elif self.tablero.jugador_muerto():
            self.game_over = True
            self.winner = "ENEMY"
            self.logs.append("¡DERROTA! El Rey Caído te ha vencido")
            self.ia.aprender_de_resultado(gano_ia=True)
