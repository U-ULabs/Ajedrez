# Ajedrez (Pygame)

Proyecto modular para practicar POO con un juego de ajedrez en Pygame, con integración de reglas vía python-chess, soporte de sonido, motores UCI locales y **juego en red LAN**.

## 📚 Wiki del Proyecto

Para documentación completa y detallada, visita la **[Wiki del Proyecto](wiki/Home.md)**:

- **[🏠 Inicio](wiki/Home.md)** - Visión general y navegación
- **[📜 Historia](wiki/Historia.md)** - Evolución y desarrollo del proyecto
- **[🛠️ Tecnologías](wiki/Tecnologia.md)** - Stack tecnológico completo
- **[🎓 Prácticas](wiki/Practicas.md)** - Metodologías y POO aplicado
- **[🏛️ Arquitectura](wiki/Arquitectura.md)** - Estructura y componentes
- **[📖 Guía de Uso](wiki/Guia-de-Uso.md)** - Instalación y manual de juego
- **[🚀 Desarrollo Futuro](wiki/Desarrollo-Futuro.md)** - Roadmap y características planificadas

## Estructura simple
- [modelos.py](file:///e:/GIT/Ajedrez/modelos.py): Color, TipoPieza, EstadoJuego y GestorRecursos (imágenes y sonidos)
- [pieza.py](file:///e:/GIT/Ajedrez/pieza.py): movimientos candidatos por tipo de pieza
- [tablero.py](file:///e:/GIT/Ajedrez/tablero.py): estado del juego y ejecución de movimientos
- [reglas.py](file:///e:/GIT/Ajedrez/reglas.py): conversión FEN, legalidad con python-chess y sugerencias UCI
- [ui.py](file:///e:/GIT/Ajedrez/ui.py): menú básico y render de tablero; temporizadores y sonido
- [lan.py](file:///e:/GIT/Ajedrez/lan.py): comunicación en red para partidas LAN (servidor y cliente)
- [main.py](file:///e:/GIT/Ajedrez/main.py): punto de entrada y bucle principal
- [docs/guia_pygame_ajedrez.md](file:///e:/GIT/Ajedrez/docs/guia_pygame_ajedrez.md): guía didáctica por etapas

## Funcionalidad implementada

### 🎮 Sistema de Menús Mejorado
- **Menú principal jerárquico** con navegación por teclado
- **Fondos de menú personalizados:**
  - `menu_classic.png` para Ajedrez Clásico
  - `menu_soul.png` para Ajedrez Sombras
  - Sistema de bucle para volver al menú principal desde cualquier modo
- **Sonido "ficha.mp3":**
  - Reproducción en navegación de menú y confirmación
  - Al mover una pieza durante la partida

### ♟️ Ajedrez Clásico
- **Múltiples modos de juego:**
  - "Jugador vs Jugador" (local)
  - "Partida LAN - Crear Servidor" (juega con blancas)
  - "Partida LAN - Unirse a Servidor" (juega con negras)
  - "Jugador vs Máquina (Stockfish)" - Motor UCI integrado
- Render del tablero y temporizadores por color
- Reglas y análisis:
  - Conversión a FEN y validación de legalidad con python-chess
  - Sugerencia de jugada vía motores UCI (Stockfish, LCZero) con niveles

### 👁️ Ajedrez Sombras (Modo RPG)
- **Sistema de combate RPG:**
  - 7 tipos de piezas con HP y daño (Peón: 20HP/5DMG ... Boss: 300HP/100DMG)
  - Combate por eliminación (no captura instantánea)
  - Barras de HP visuales con código de colores (verde/amarillo/rojo)
  - Números de HP visibles (ej: "50/100")
- **Presentación visual mejorada:**
  - Usa imágenes PNG de piezas del ajedrez clásico
  - **Boss con imagen especial** (`boss.png`) y borde dorado
  - Efectos visuales distintivos para el Rey Caído
- **Mecánicas de juego:**
  - Niebla de guerra (visibilidad 3x3 alrededor del Rey)
  - Boss IA con táctica de invocación (30% por turno)
  - Victoria al derrotar al Boss, derrota si cae tu Rey
- **Sistema de juego en red LAN:**
  - Comunicación cliente-servidor mediante sockets TCP
  - Protocolo JSON para sincronización de movimientos
  - Servidor escucha en puerto 8080 y juega con blancas
  - Cliente se conecta a IP del servidor y juega con negras
  - Sincronización en tiempo real entre equipos

## Requisitos
- Python 3.10+
- pygame
- requests
- python-chess
- chess-engine (opcional; el código usa `chess.engine` de python-chess)

Instala con:
```
pip install -r requirements.txt
```

## Ejecución
```
python main.py
```
- Coloca imágenes (opcional) en `images/` con nombres esperados (p.ej. reina_blanca.png).
- Coloca el fondo del menú (opcional) en `images/menu.png`.
- Coloca el sonido en `sounds/ficha.mp3`. Si falta, el juego continúa sin sonido.

## Jugar en red LAN

**Para crear un servidor (jugador con blancas):**
1. Ejecuta `python main.py`
2. Selecciona "Partida LAN - Crear Servidor"
3. Obtén tu IP local:
   - Windows: `ipconfig` en CMD (busca "Dirección IPv4")
   - Linux/Mac: `ifconfig` o `ip addr`
4. Comunica tu IP al otro jugador
5. Espera la conexión (máximo 60 segundos)
6. ¡Comienza a jugar!

**Para conectarse a un servidor (jugador con negras):**
1. Ejecuta `python main.py`
2. Selecciona "Partida LAN - Unirse a Servidor"
3. Introduce la IP del servidor cuando se solicite
4. Espera confirmación de conexión
5. ¡Comienza a jugar!

**Configuración de firewall:**
- El servidor debe permitir conexiones entrantes en el puerto 8080
- En Windows: Panel de Control > Sistema y Seguridad > Firewall de Windows
- Crear regla de entrada para permitir puerto TCP 8080

**Notas importantes:**
- Ambos equipos deben estar en la misma red local (LAN)
- El servidor siempre juega con blancas, el cliente con negras
- Los movimientos se sincronizan automáticamente
- Si se pierde la conexión, la partida termina

## Motores UCI (opcional)
- Coloca `stockfish.exe` y/o `lc0.exe` accesibles (PATH o junto al proyecto).
- Usa [reglas.py](file:///e:/GIT/Ajedrez/reglas.py) para sugerir jugadas:
```python
from reglas import sugerir_movimiento
lan = sugerir_movimiento(casillas, turno, motor="stockfish", nivel="medio")
```
- Niveles: `facil` (~200 ms), `medio` (~500 ms), `dificil` (~2000 ms).

## Notas
- El menú actualmente ofrece el modo local entre dos jugadores. La guía incluye pasos para extender a IA y APIs.
- El GestorRecursos tolera faltantes: crea placeholders y deshabilita sonido si `pygame.mixer` no está disponible.
