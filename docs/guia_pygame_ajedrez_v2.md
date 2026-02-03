# Guía Técnica: Arquitectura modular de Ajedrez v2.0

## 📋 Resumen Ejecutivo

Este documento describe la arquitectura final de **Ajedrez v2.0**, un proyecto Pygame modular que implementa:
1. **Ajedrez Clásico**: Juego tradicional con 4 modos (Local, LAN 2/Cliente, vs IA Stockfish)
2. **Ajedrez Sombras**: Variante RPG con niebla de guerra, sistema de HP/Daño y Boss IA

Estado actual: ✅ **Completamente funcional**

---

## 🏗️ Arquitectura del Proyecto

### Estructura de Módulos

```
Ajedrez/
│
├── [PUNTO DE ENTRADA]
│   └── main.py                    # Menú jerárquico + orquestación de modos
│
├── [MÓDULO CLÁSICO]
│   └── ajedrez_clasico/
│       ├── __init__.py            # Exporta Tablero, Pieza
│       ├── tablero.py             # Lógica de juego (turnos, jaque/mate)
│       └── pieza.py               # 6 tipos de piezas + movimientos
│
├── [MÓDULO SOMBRAS - RPG]
│   └── ajedrez_sombras/
│       ├── __init__.py            # Exporta TableroSombras, IASombras
│       ├── constantes.py          # Stats RPG, colores, configuración
│       ├── pieza_sombras.py       # 7 tipos (Peón...Rey, Boss)
│       ├── tablero_sombras.py     # Tablero + niebla de guerra
│       └── ia_sombras.py          # Boss IA + táctica de invocación
│
├── [UTILIDADES COMPARTIDAS]
│   ├── modelos.py                 # Enums: Color, TipoPieza, EstadoJuego
│   ├── ui.py                      # Menu, InterfazUsuario (ambos modos)
│   ├── reglas.py                  # Motores UCI (Stockfish)
│   └── lan.py                     # Red LAN (TCP/UDP)
│
├── [RECURSOS]
│   ├── requirements.txt           # pygame-ce 2.5.6, python-chess 1.999
│   ├── docs/                      # Documentación
│   ├── images/                    # Assets visuales
│   ├── sounds/                    # Assets de audio
│   └── stockfish/                 # Binarios de motor UCI (opcional)
```

---

## 🔄 Flujo de Control Principal

### Menú Jerárquico (main.py) - Sistema Mejorado v2.1

```
┌─────────────────────────────────────┐
│   AJEDREZ - MENÚ PRINCIPAL          │
├─────────────────────────────────────┤
│  [MODO]  [OPCIÓN]                   │
│  ├─ AJEDREZ CLÁSICO                │
│  │  ├─ Jugador vs Jugador          │ ← juego_local()
│  │  ├─ LAN Servidor                │ ← juego_lan_servidor()
│  │  ├─ LAN Cliente                 │ ← juego_lan_cliente()
│  │  ├─ vs Máquina (Stockfish)      │ ← juego_vs_maquina()
│  │  └─ Volver                      │ ← Regresa al menú principal
│  │                                  │
│  └─ AJEDREZ SOMBRAS (RPG)          │
│     ├─ Vs Boss IA                  │ ← juego_sombras()
│     └─ Volver                      │ ← Regresa al menú principal
│                                     │
│  Salir                              │ ← Cierra el juego
└─────────────────────────────────────┘
```

**Navegación mejorada (v2.1):**
- `↑ ↓` : Cambiar opción
- `ENTER` : Seleccionar
- **Bucle principal**: Opción "Volver" regresa al menú sin cerrar el juego
- **Fondos personalizados**:
  - `menu_classic.png` - Fondo para menú de Ajedrez Clásico
  - `menu_soul.png` - Fondo para menú de Ajedrez Sombras
  - Carga dinámica según parámetro `modo` en clase `Menu`

### Sistema de Menús (ui.py - Menu)

```python
class Menu:
    def __init__(self, opciones: List[str], modo: str = "default"):
        """Inicializa menú con fondo personalizado.
        
        Args:
            opciones: Lista de opciones del menú
            modo: "default", "classic", o "soul" (determina imagen de fondo)
        """
        # Cargar imagen de fondo según modo
        if modo == "classic":
            nombre_fondo = "menu_classic.png"
        elif modo == "soul":
            nombre_fondo = "menu_soul.png"
        else:
            nombre_fondo = "menu.png"
        
        # Cargar y escalar imagen
        ruta_fondo = os.path.join(self.gestor.directorio_imagenes, nombre_fondo)
        fondo = pygame.image.load(ruta_fondo).convert()
        self._fondo_menu = pygame.transform.scale(fondo, self.pantalla.get_size())
    
    def loop(self) -> Optional[str]:
        """Bucle del menú con navegación por teclado."""
        while True:
            # Dibujar fondo personalizado
            if self._fondo_menu:
                self.pantalla.blit(self._fondo_menu, (0, 0))
            
            # Renderizar opciones
            for idx, texto in enumerate(self.opciones):
                color = (255, 255, 255) if idx == self.seleccion else (180, 180, 180)
                superficie = self.fuente.render(texto, True, color)
                self.pantalla.blit(superficie, (60, 60 + idx * 50))
```

**Uso en main.py:**
```python
# Menú clásico con fondo personalizado
menu_clasico = Menu([
    "Jugador vs Jugador",
    "Partida LAN - Crear Servidor",
    "Partida LAN - Unirse a Servidor",
    "Jugador vs Máquina (Stockfish)",
    "Volver"
], modo="classic")  # Carga menu_classic.png

# Menú sombras con fondo personalizado
menu_sombras = Menu([
    "Jugador vs Boss IA",
    "Volver"
], modo="soul")  # Carga menu_soul.png
```
└─────────────────────────────────────┘
```

**Navegación:**
- `↑ ↓` : Cambiar opción dentro de modo actual
- `← →` : Cambiar modo
- `ENTER` : Seleccionar opción
- `ESC` : Volver/Salir

---

## 🎮 Ajedrez Clásico - Arquitectura

### 1. Modelo de Datos (ajedrez_clasico/pieza.py)

```python
# 6 clases de piezas (heredan de Pieza base)
class Pieza:
    """Base con tipo, color, posición, movimientos."""
    def obtener_movimientos_validos(tablero) -> List[Tuple[int,int]]

class Peon(Pieza):      # Movimiento 1 (2 inicial), captura diagonal
class Caballo(Pieza):   # Movimiento en L (2+1)
class Alfil(Pieza):     # Movimiento diagonal ilimitado
class Torre(Pieza):     # Movimiento H/V ilimitado
class Reina(Pieza):     # Torre + Alfil combinados
class Rey(Pieza):       # Movimiento 1 paso (todas direcciones)
```

**Atributos clave:**
- `tipo` (TipoPieza): Enum con 6 valores
- `color` (Color): BLANCO o NEGRO
- `posicion` (Tuple[int,int]): (x 0-7, y 0-7)
- `imagen` (pygame.Surface): Renderización

---

### 2. Estado del Juego (ajedrez_clasico/tablero.py)

```python
class Tablero:
    """8x8 casillas, turno, historial, validación de jaque/mate."""
    
    def __init__(self):
        self.casillas: Dict[Tuple[int,int], Optional[Pieza]] = {}
        self.turno = Color.BLANCO
        self.estado = EstadoJuego.JUGANDO  # o JAQUE, JAQUE_MATE, TABLAS
        self.historial = []
    
    def inicializar(self):
        """Coloca piezas en posición inicial."""
    
    def realizar_movimiento(origen, destino) -> bool:
        """Valida y ejecuta movimiento. Retorna éxito."""
    
    def esta_en_jaque(color) -> bool:
        """Verifica si Rey del color está atacado."""
    
    def es_jaque_mate(color) -> bool:
        """Verifica si Rey está en jaque y sin movimientos válidos."""
```

---

### 3. Validación de Reglas (reglas.py)

```python
def tablero_a_fen(casillas, turno) -> str:
    """Convierte diccionario de casillas a FEN para python-chess."""

def aplicar_movimiento_lan(tablero, lan: str) -> bool:
    """Aplica movimiento notación LAN (e2e4) al tablero."""

def sugerir_movimiento(casillas, turno, motor="stockfish", nivel="medio") -> str:
    """Consulta motor UCI y retorna mejor movimiento en LAN."""
```

---

### 4. Interfaz Gráfica (ui.py - InterfazUsuario)

**Renderización:**
- Tablero 8x8 con casillas alternas (claro/oscuro)
- Piezas representadas como superficies coloreadas con letra
- Selección resaltada en verde
- Movimientos válidos marcados

**Entrada del usuario:**
- Click en casilla → coordenadas grid (x, y)
- Primer click: selecciona pieza
- Segundo click: confirma destino

**Temporizadores:**
- Reloj por color (mm:ss)
- Pausa cuando no es turno

---

### 5. Modos de Juego (main.py)

#### 5.1 Jugador vs Jugador - juego_local()
```python
def juego_local():
    tablero = Tablero()
    interfaz = InterfazUsuario(tablero)
    
    while True:
        for event in pygame.event.get():
            # Manejar click → selección → movimiento
            origen, destino = interfaz.manejar_eventos()
            if tablero.realizar_movimiento(origen, destino):
                tablero.turno = Color.NEGRO if turno == Color.BLANCO else Color.BLANCO
        
        interfaz.dibujar_tablero()
        if tablero.estado == EstadoJuego.JAQUE_MATE:
            break
```

#### 5.2 LAN Servidor - juego_lan_servidor()
```python
def juego_lan_servidor():
    servidor = ServidorAjedrez(puerto=8880)
    servidor.iniciar()
    interfaz.mensaje_estado = "Esperando cliente..."
    
    if servidor.esperar_conexion(timeout=60):
        # Juega con blancas, recibe movimientos del cliente
        while True:
            # Humano mueve (blancas), envía al cliente
            # Recibe respuesta de cliente (negras)
            # Verifica fin de partida
```

#### 5.3 LAN Cliente - juego_lan_cliente()
```python
def juego_lan_cliente():
    cliente = ClienteAjedrez()
    if cliente.conectar(host=ip_servidor, puerto=8880):
        # Juega con negras, espera movimientos del servidor
        while True:
            # Espera movimiento del servidor (blancas)
            # Humano mueve (negras), envía al servidor
            # Verifica fin de partida
```

**Protocolo LAN:**
```json
{
  "tipo": "movimiento",
  "origen": [4, 6],
  "destino": [4, 4],
  "turno": "blanco"
}
```

#### 5.4 vs Máquina - juego_vs_maquina()
```python
def juego_vs_maquina():
    tablero = Tablero()
    interfaz = InterfazUsuario(tablero)
    
    while True:
        if tablero.turno == Color.BLANCO:  # Jugador
            origen, destino = interfaz.manejar_eventos()
            tablero.realizar_movimiento(origen, destino)
        else:  # IA Stockfish
            interfaz.mensaje_estado = "Pensando..."
            fen = tablero_a_fen(tablero.casillas, tablero.turno)
            lan = sugerir_movimiento(fen, nivel="medio")
            tablero.realizar_movimiento(*lan_a_coords(lan))
```

---

## 🌑 Ajedrez Sombras - Arquitectura RPG

### 1. Sistema de Piezas con HP/Daño y Visualización Mejorada

```python
class PiezaSombra(pygame.sprite.Sprite):
    """Pieza base con sistema RPG y renderizado visual mejorado.
    
    Atributos:
        - hp, hp_max: Puntos de vida
        - damage: Daño por ataque
        - es_boss: True solo para el Rey Caído
        - gestor_recursos: Para cargar imágenes PNG (nuevo en v2.1)
    """
    
    def __init__(self, grid_x, grid_y, team, tipo_key, gestor_recursos=None):
        # Cargar estadísticas RPG
        stats = STATS.get(tipo_key, STATS["PEON"])
        self.hp_max = stats["hp"]
        self.hp = self.hp_max
        self.damage = stats["dmg"]
        
        # MEJORA v2.1: Cargar imagen real o usar rectángulo legacy
        if gestor_recursos:
            self._cargar_imagen_pieza()  # Usa PNG del ajedrez clásico
        else:
            self._crear_imagen_legacy()  # Rectángulo de color
    
    def _cargar_imagen_pieza(self):
        """Carga imagen PNG según tipo y equipo."""
        # Si es Boss → usa boss.png
        if self.es_boss:
            clave_imagen = "BOSS"
        else:
            # Ejemplo: "TORRE_BLANCO", "CABALLO_NEGRO"
            color_equipo = "BLANCO" if self.team == TEAM_PLAYER else "NEGRO"
            clave_imagen = f"{self.tipo}_{color_equipo}"
        
        imagen_base = self.gestor_recursos.imagenes.get(clave_imagen)
        
        # Crear superficie con espacio para barra de HP
        self.image = pygame.Surface((TILE_SIZE - 10, TILE_SIZE - 10), pygame.SRCALPHA)
        img_escalada = pygame.transform.scale(imagen_base, (TILE_SIZE - 15, TILE_SIZE - 25))
        self.image.blit(img_escalada, (2, 5))
        
        # Si es Boss, agregar borde dorado especial
        if self.es_boss:
            pygame.draw.rect(self.image, YELLOW, self.image.get_rect(), 3)
    
    def dibujar_barra_hp(self, superficie):
        """Dibuja barra de HP didáctica sobre la pieza.
        
        Características:
        - Verde (>60% HP), Amarilla (30-60%), Roja (<30%)
        - Muestra números: "HP actual/HP máximo"
        - Borde dorado para el Boss
        """
        # Calcular posición y tamaño
        barra_ancho = TILE_SIZE - 15
        barra_alto = 5
        barra_x = self.rect.x + 2
        barra_y = self.rect.y - 8
        
        # Color según porcentaje de HP
        porcentaje_hp = self.hp / self.hp_max
        if porcentaje_hp > 0.6:
            color_hp = GREEN
        elif porcentaje_hp > 0.3:
            color_hp = YELLOW
        else:
            color_hp = RED
        
        # Dibujar fondo negro + HP actual
        pygame.draw.rect(superficie, BLACK, (barra_x, barra_y, barra_ancho, barra_alto))
        ancho_hp = int(barra_ancho * porcentaje_hp)
        if ancho_hp > 0:
            pygame.draw.rect(superficie, color_hp, (barra_x, barra_y, ancho_hp, barra_alto))
        
        # Borde (dorado para Boss, blanco para otros)
        if self.es_boss:
            pygame.draw.rect(superficie, YELLOW, (barra_x - 1, barra_y - 1, barra_ancho + 2, barra_alto + 2), 2)
        else:
            pygame.draw.rect(superficie, WHITE, (barra_x, barra_y, barra_ancho, barra_alto), 1)
        
        # Mostrar texto "HP actual/HP máximo"
        font = pygame.font.SysFont("Arial", 8, bold=True)
        texto_hp = f"{self.hp}/{self.hp_max}"
        text_surface = font.render(texto_hp, True, WHITE)
        # Sombra para legibilidad
        shadow_surface = font.render(texto_hp, True, BLACK)
        superficie.blit(shadow_surface, (text_rect.x + 1, text_rect.y + 1))
        superficie.blit(text_surface, text_rect)
    """Base con estadísticas RPG."""
    
    def __init__(self, grid_x, grid_y, team, tipo_key):
        self.grid_x, self.grid_y = grid_x, grid_y
        self.team = team  # JUGADOR o ENEMIGO
        self.tipo = tipo_key  # "PEON", "CABALLO", etc.
        self.es_boss = False  # True solo para Rey Caído
        
        # Stats RPG
        stats = STATS[tipo_key]
        self.hp_max = stats["hp"]
        self.hp = self.hp_max
        self.damage = stats["dmg"]
    
    def recibir_damage(cantidad) -> bool:
        """Reduce HP. Retorna True si pieza muere."""
        self.hp -= cantidad
        if self.hp <= 0:
            self.kill()  # Elimina del tablero
            return True
        return False
```

**7 Clases de Piezas:**

| Clase | Nombre | HP | DMG | Movimiento |
|---|---|---|---|---|
| PiezaSombraPeon | Hueco | 20 | 10 | Limitado (1-2 casillas) |
| PiezaSombraCaballo | Caballero | 40 | 20 | En L (salta) |
| PiezaSombraAlfil | Hechicero | 30 | 25 | Diagonal |
| PiezaSombraTorre | Torre | 60 | 15 | H/V |
| PiezaSombraReina | Reina | 80 | 30 | 8 direcciones |
| PiezaSombraRey | Rey | 100 | 40 | 1 paso |
| PiezaSombraRey (es_boss=True) | **Rey Caído** | **300** | **50** | 1 paso, invoca |

---

### 2. Tablero con Niebla de Guerra (ajedrez_sombras/tablero_sombras.py)

```python
class TableroSombras:
    """8x8 con niebla de guerra (visión 3x3 del Rey)."""
    
    def __init__(self):
        self.piezas = []  # Sprite group
        self.niebla = [[True]*8 for _ in range(8)]  # Matriz de ocultamiento
        self.inicializar_sombras()
    
    def actualizar_niebla(self):
        """Actualiza visibilidad: marca 3x3 alrededor del Rey como visible."""
        rey = [p for p in self.piezas if p.team == TEAM_PLAYER and isinstance(p, PiezaSombraRey)][0]
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = rey.grid_x + dx, rey.grid_y + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    self.niebla[y][x] = False  # Visible
    
    def es_visible(x, y) -> bool:
        """Retorna True si casilla está visible (no en niebla)."""
        return not self.niebla[y][x]
    
    def boss_muerto() -> bool:
        """Verifica si Rey Caído está muerto (victoria)."""
        for pieza in self.piezas:
            if pieza.team == TEAM_ENEMY and pieza.es_boss:
                return False  # Boss vivo
        return True  # Boss muerto = Victoria
```

**Mecánica de Niebla:**
- Visión centrada en Rey del Jugador (3x3 alrededor)
- Enemigos fuera de la niebla NO se renderizan
- Movimientos de enemigos en la niebla son ocultos hasta entrar en rango

---

### 3. IA del Boss (ajedrez_sombras/ia_sombras.py)

```python
class IASombras:
    """IA del Boss Rey Caído con táctica de invocación."""
    
    def turno_ia(tablero) -> bool:
        """Ejecuta turno del Boss. Retorna True si movió."""
        
        # 30% chance: Invoca una sombra (nueva pieza)
        if random.random() < 0.3:
            self.invocar_sombra(tablero)
            return True
        
        # Táctica: Atacar Rey del jugador si está visible
        rey_jugador = self.obtener_rey(tablero, TEAM_PLAYER)
        piezas_atacantes = self.piezas_pueden_atacar(tablero, rey_jugador.posicion)
        if piezas_atacantes:
            pieza = piezas_atacantes[0]
            destino = rey_jugador.posicion
            self.mover_pieza(pieza, destino, tablero)
            return True
        
        # Fallback: Movimiento aleatorio de una pieza
        pieza = random.choice(self.piezas_vivas(tablero))
        movimientos = pieza.obtener_movimientos_validos(tablero)
        if movimientos:
            self.mover_pieza(pieza, random.choice(movimientos), tablero)
            return True
        
        return False  # Sin movimientos posibles
```

**Invocación de Sombras:**
- Cada turno IA: 30% chance de invocar nueva pieza
- Pieza elegida aleatoria (Peón, Caballo, Alfil)
- Aparecer en zona controlada del Boss (lado enemigo del tablero)
- Máximo de piezas: 8 (después no invoca)

---

### 4. Sistema de Combate (tablero_sombras.py)

```python
def resolver_combate(atacante: PiezaSombra, defensor: PiezaSombra):
    """Combate: atacante vs defensor."""
    
    # Atacante inflige daño
    danyo = atacante.damage
    
    # Defensor recibe daño
    murio = defensor.recibir_damage(danyo)
    
    if murio:
        print(f"{defensor.nombre} ({defensor.team}) fue destruido por {atacante.nombre}")
        return True
    else:
        print(f"{defensor.nombre} ahora tiene {defensor.hp}/{defensor.hp_max} HP")
        return False
```

**Reglas de combate:**
- No hay retaliación (solo atacante inflige daño)
- Defensor puede estar en 0 HP (muere inmediatamente)
- Si Rey muere → Derrota
- Si Boss muere → Victoria

---

### 5. Modo Jugador vs Boss (main.py - juego_sombras())

```python
def juego_sombras():
    """Modo Sombras: Jugador (Azul) vs Boss IA (Rojo)."""
    
    # MEJORA v2.1: Cargar gestor de recursos para imágenes
    from modelos import GestorRecursos
    gestor = GestorRecursos()
    
    # Crear tablero con gestor (activa imágenes PNG)
    tablero = TableroSombras(gestor_recursos=gestor)
    ia = IASombras(tablero)
    
    pantalla = pygame.display.set_mode((800, 600))
    turno = "JUGADOR"
    
    while corriendo:
        # Turno del Jugador: Click para seleccionar/mover
        if turno == "JUGADOR":
            # Manejar eventos de mouse
            # Si movimiento válido → cambiar a turno "ENEMIGO"
        
        # Turno de la IA
        if turno == "ENEMIGO":
            ia.invocar_sombra()  # 30% chance
            movimiento = ia.calcular_movimiento()
            if movimiento:
                tablero.mover_pieza(*movimiento)
            turno = "JUGADOR"
        
        # Dibujar tablero
        pantalla.fill((30, 30, 30))
        tablero.dibujar(pantalla)
        
        # MEJORA v2.1: Dibujar barras de HP sobre todas las piezas
        for pieza in tablero.piezas:
            pieza.dibujar_barra_hp(pantalla)
        
        pygame.display.flip()
        
        # Verificar condiciones de victoria/derrota
        if tablero.boss_muerto():
            print("¡VICTORIA! Derrotaste al Rey Caído")
            break
        elif tablero.jugador_muerto():
            print("¡DERROTA! El Rey Caído te venció")
            break
```

**Elementos visuales v2.1:**
- ✅ Imágenes PNG de piezas clásicas
- ✅ Boss con imagen especial (`boss.png`) y doble borde dorado
- ✅ Barras de HP con código de colores (verde/amarillo/rojo)
- ✅ Números de HP visibles ("50/100")
- ✅ Presentación didáctica y profesional
    ia = IASombras()
    turno = TEAM_PLAYER
    
    while True:
        # Actualizar niebla (visión del jugador)
        tablero.actualizar_niebla()
        
        if turno == TEAM_PLAYER:
            # Entrada: click → seleccionar pieza → destino
            pieza, destino = interfaz.obtener_entrada_jugador()
            if pieza and destino in pieza.obtener_movimientos_validos(tablero):
                # Ejecutar movimiento + combate si hay
                destino_pieza = tablero.obtener_pieza_en(destino)
                if destino_pieza and destino_pieza.team != pieza.team:
                    resolver_combate(pieza, destino_pieza)  # Ataque
                else:
                    pieza.grid_x, pieza.grid_y = destino  # Movimiento simple
                turno = TEAM_ENEMY
        else:
            # IA mueve
            if ia.turno_ia(tablero):
                turno = TEAM_PLAYER
        
        # Renderizar
        interfaz.dibujar_tablero_sombras(tablero)
        
        # Verificar fin de partida
        if tablero.boss_muerto():
            interfaz.mostrar_victoria()
            break
        if interfaz.obtener_rey(tablero, TEAM_PLAYER) is None:
            interfaz.mostrar_derrota()
            break
```

---

## 🔧 Análisis de Dependencias

### Grafo de Importes

```
main.py
├── ui.py
│   └── ajedrez_clasico/
│       ├── tablero.py
│       ├── pieza.py
│       └── modelos.py
├── modelos.py
├── reglas.py
│   ├── modelos.py
│   ├── ajedrez_clasico/pieza.py
│   └── [python-chess]
├── lan.py
│   └── modelos.py
└── ajedrez_sombras/
    ├── tablero_sombras.py
    │   ├── constantes.py
    │   ├── pieza_sombras.py
    │   └── ia_sombras.py
    ├── ia_sombras.py
    │   └── pieza_sombras.py
    └── constantes.py
```

### Librerías Externas

| Librería | Versión | Uso |
|---|---|---|
| pygame-ce | 2.5.6 | Renderización gráfica, eventos |
| python-chess | 1.999 | Validación FEN, motores UCI |

### Librerías Estándar (No requieren pip)

- `socket` - Comunicación TCP/UDP (LAN)
- `threading` - Hilos asincronos
- `json` - Serialización de mensajes
- `enum` - Enumeraciones
- `subprocess` - Ejecución de motores UCI
- `random` - Toma de decisiones IA

---

## 📝 Cambios Recientes (v2.0)

### ✅ Correcciones

1. **Error `'PiezaSombraTorre' object has no attribute 'es_boss'`**
   - Causa: Atributo `es_boss` solo definido en `PiezaSombraRey`, no en clase base
   - Solución: Agregado `self.es_boss = False` en `PiezaSombra.__init__`
   - Verificación: Todos los imports resueltos ✓

2. **Imports incorrectos**
   - Antes: `from pieza import Pieza` (importación absoluta)
   - Después: `from .pieza import Pieza` o `from ajedrez_clasico import Pieza` (relativa/módulo)

### ⬆️ Mejoras de Código

1. **Documentación extendida**
   - Constantes.py: Secciones con comentarios detallados (Pantalla, Tablero, Colores, Stats)
   - Pieza_sombras.py: Docstrings completos en cada clase con ejemplos

2. **Requirements.txt actualizado**
   - `pygame-ce>=2.5.6` (último para Python 3.14+)
   - Secciones: Motor Gráfico, Motores Ajedrez, Librerías Opcionales

3. **README.md v2.0**
   - Tabla de estado (✅ Completamente funcional)
   - Detalles de cada módulo
   - Cambios recientes documentados

---

## 🎯 Testing y Validación

### Checklist de Verificación

```bash
# 1. Syntax check
.\.venv\Scripts\python.exe -m py_compile main.py

# 2. Import verification
.\.venv\Scripts\python.exe -c "
from ui import Menu
from ajedrez_clasico import Tablero
from ajedrez_sombras import TableroSombras, IASombras
print('✓ Todos los imports funcionan')
"

# 3. Ejecución
.\.venv\Scripts\python.exe main.py
# Navegar por menús
# Verificar ambos modos funcionan
```

---

## 🚀 Objetivos Futuros

| Objetivo | Prioridad | Notas |
|---|---|---|
| Guardar/cargar partidas (pickle) | Media | Serializar estado del tablero |
| IA mejorada (Minimax + Alpha-Beta) | Media | Mejor desempeño vs Stockfish |
| Base de datos de aperturas | Baja | Libro de aperturas integrado |
| Tema personalizable | Baja | Opciones de colores/estilos |
| API Chess.com | Baja | Integración con perfiles/ratings |

---

## 📚 Referencias y Recursos

- [Pygame Docs](https://www.pygame.org/docs/)
- [python-chess](https://python-chess.readthedocs.io/)
- [Stockfish UCI](https://stockfishchess.org/)
- [Chess.com API](https://www.chess.com/news/view/published-data-api)

---

## 👤 Información del Proyecto

**Versión:** 2.0  
**Estado:** ✅ Funcional  
**Última actualización:** 2 de febrero de 2026  
**Rama:** UI_LAN  
**Owner:** U-ULabs
