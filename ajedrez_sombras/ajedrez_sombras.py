import pygame
from .tablero_sombras import TableroSombras
from .ia_sombras import IASombras
from .constantes import BOARD_OFFSET_X, BOARD_OFFSET_Y, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from modelos import GestorRecursos

def juego_sombras():
    """Ejecuta una partida en modo Sombras (Jugador vs Boss IA)."""
    print("\n=== INICIANDO AJEDREZ SOMBRAS ===")
    print("Eres el AZUL (Jugador). Tu enemigo es el ROJO (Boss Enemigo).")
    print("¡Objetivos: Explora, lucha, y derrota al Rey Caído!\n")
    
    # MEJORA 14: Crear gestor de recursos para cargar imágenes de piezas
    gestor = GestorRecursos()
    
    # MEJORA 15: Pasar gestor al TableroSombras para usar imágenes reales
    tablero = TableroSombras(gestor_recursos=gestor)
    ia = IASombras(tablero)
    
    # Crear UI (simplificada para Sombras)
    pantalla = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Ajedrez de las Sombras")
    clock = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial", 16)
    
    turno = "JUGADOR"
    pieza_seleccionada = None
    
    corriendo = True
    while corriendo:
        clock.tick(30)
        
        # Procesar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
            
            elif evento.type == pygame.MOUSEBUTTONDOWN and turno == "JUGADOR":
                # Click del jugador
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                grid_x = (mouse_x - BOARD_OFFSET_X) // TILE_SIZE
                grid_y = (mouse_y - BOARD_OFFSET_Y) // TILE_SIZE
                
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    pieza_en_casilla = tablero.obtener_pieza_en(grid_x, grid_y)
                    
                    if pieza_seleccionada is None:
                        # Seleccionar pieza del jugador
                        if pieza_en_casilla and pieza_en_casilla.team == "JUGADOR":
                            pieza_seleccionada = pieza_en_casilla
                            print(f"Seleccionado: {pieza_en_casilla.nombre} en ({grid_x}, {grid_y})")
                    else:
                        # Intentar mover a destino
                        if pieza_en_casilla == pieza_seleccionada:
                            # Deseleccionar
                            pieza_seleccionada = None
                        else:
                            # Mover si es movimiento válido
                            movimientos_validos = pieza_seleccionada.obtener_movimientos_validos(tablero)
                            if (grid_x, grid_y) in movimientos_validos:
                                tablero.mover_pieza(pieza_seleccionada, grid_x, grid_y)
                                print(f"{pieza_seleccionada.nombre} se movió a ({grid_x}, {grid_y})")
                                pieza_seleccionada = None
                                turno = "ENEMIGO"
                            else:
                                # Seleccionar otra pieza
                                if pieza_en_casilla and pieza_en_casilla.team == "JUGADOR":
                                    pieza_seleccionada = pieza_en_casilla
                                    print(f"Seleccionado: {pieza_en_casilla.nombre} en ({grid_x}, {grid_y})")
                                else:
                                    pieza_seleccionada = None
        
        # Turno de la IA
        if turno == "ENEMIGO":
            # Invocar sombra (30% probabilidad)
            ia.invocar_sombra()
            
            # Calcular movimiento
            movimiento = ia.calcular_movimiento()
            if movimiento:
                pieza, x, y = movimiento
                tablero.mover_pieza(pieza, x, y)
                print(f"IA movió {pieza.nombre} a ({x}, {y})")
            
            turno = "JUGADOR"
        
        # Verificar condiciones de victoria/derrota
        if tablero.boss_muerto():
            print("\n¡¡¡ VICTORIA !!! ¡Has derrotado al Rey Caído!")
            ia.aprender_de_resultado(gano_ia=False)
            corriendo = False
        elif tablero.jugador_muerto():
            print("\n¡¡¡ DERROTA !!! El Rey Caído te ha vencido.")
            ia.aprender_de_resultado(gano_ia=True)
            corriendo = False
        
        # Dibujar
        pantalla.fill((30, 30, 30))
        
        # Dibujar tablero
        tablero.dibujar(pantalla)
        
        # MEJORA 16: Dibujar barras de HP didácticas sobre todas las piezas
        for pieza in tablero.piezas:
            pieza.dibujar_barra_hp(pantalla)
        
        # Dibujar información
        info_turno = f"Turno: {turno}"
        info_text = fuente.render(info_turno, True, (255, 255, 255))
        pantalla.blit(info_text, (10, 10))
        
        pygame.display.flip()
    
    print("\nFin de la partida.\n")
