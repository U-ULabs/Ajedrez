# Roadmap Ajedrez v2.0 - Estado y Visión

## 📊 Estado Actual (v2.1 - Febrero 2026)

### ✅ COMPLETADO

#### Core Ajedrez Clásico
- ✅ Estructura modular completa (ajedrez_clasico/, ajedrez_sombras/)
- ✅ 6 tipos de piezas con movimientos válidos
- ✅ Tablero 8x8, sistema de turnos, jaque/jaque mate
- ✅ Validación de reglas con python-chess
- ✅ FEN ↔ Tablero conversión

#### Modos de Juego - Ajedrez Clásico (4/4)
- ✅ **Modo 1: Jugador vs Jugador (Local)**
  - Click-select UI
  - Temporizadores por color
  - Victoria/derrota detectada automáticamente

- ✅ **Modo 2: LAN Servidor**
  - Puerto 8880 (TCP)
  - Espera 60s con countdown overlay
  - Juega con blancas
  - Protocolo JSON de movimientos

- ✅ **Modo 3: LAN Cliente**
  - Auto-discovery (UDP 8888)
  - Conexión manual fallback
  - Juega con negras
  - Sincronización en tiempo real

- ✅ **Modo 4: vs Máquina (Stockfish)**
  - Motor UCI integrado
  - "Pensando..." UI durante búsqueda
  - Nivel configurable (fácil/medio/difícil)

#### Ajedrez Sombras - Variante RPG (1/1)
- ✅ Sistema RPG con 7 tipos de piezas
- ✅ HP/Daño por pieza (Peón 20HP...Rey Caído 300HP)
- ✅ Niebla de guerra (3x3 alrededor del Rey)
- ✅ Combate eliminatorio (no captura clásica)
- ✅ Boss IA con táctica de invocación (30% por turno)
- ✅ Victoria/Derrota detectadas
- ✅ Menú jerárquico integrado
- ✅ **Sistema visual mejorado:**
  - Imágenes PNG de piezas clásicas integradas
  - Imagen especial del Boss (boss.png) con borde dorado
  - Barras de HP visuales con código de colores (verde/amarillo/rojo)
  - Números de HP visibles sobre cada pieza
  - Presentación didáctica y profesional

#### Sistema de Menús y Navegación
- ✅ Menú principal jerárquico con bucle de retorno
- ✅ Fondos personalizados por modo:
  - menu_classic.png para Ajedrez Clásico
  - menu_soul.png para Ajedrez Sombras
- ✅ Navegación por teclado con sonido
- ✅ Sistema modular de Menú con parámetro 'modo'

#### Documentación y Código
- ✅ Comentarios extensos en ajedrez_sombras/
- ✅ Docstrings detallados en todas las clases
- ✅ requirements.txt actualizado (pygame-ce 2.5.6)
- ✅ README.md v2.0 con tablas de estado
- ✅ Guía Técnica v2.0 (arquitectura completa)
- ✅ Fix: Error 'es_boss' en PiezaSombraTorre

#### Validación
- ✅ py_compile: Sintaxis OK
- ✅ Import chain: Todos los módulos importan correctamente
- ✅ Ejecución: main.py inicia sin errores

---

## 🎯 Visión a Corto Plazo (v2.1 - Próximos 30 días)

### 1. Mejoras de IA (Prioridad MEDIA)
- [ ] Implementar Minimax + Alpha-Beta Pruning
- [ ] Evaluación de posición más sofisticada
- [ ] Apertura con libro de aperturas integrado
- [ ] Niveles de dificultad expandidos (5 en lugar de 3)

**Impacto:** Juego vs IA más desafiante y realista

### 2. Guardar/Cargar Partidas (Prioridad MEDIA)
- [ ] Serializar estado de Tablero con pickle
- [ ] Guardar en formato PGN estándar
- [ ] Historial de movimientos anotado (SAN: e2-e4)
- [ ] Resaltado de última jugada en UI

**Impacto:** Continuidad de partidas, análisis posterior

### 3. Mejoras de UI/UX (Prioridad MEDIA)
- [ ] Resaltado visual del jaque
- [ ] Indicador visual de turno (LED/banner)
- [ ] Animación de movimientos (transición suave)
- [ ] Panel de información: última jugada, reloj, estado
- ✅ **Sistema visual para Ajedrez Sombras** (COMPLETADO v2.1)
  - Barras de HP con código de colores
  - Imágenes de piezas integradas
  - Efectos visuales para el Boss
- ✅ **Menús con fondos personalizados** (COMPLETADO v2.1)

**Impacto:** Experiencia de usuario mejorada

### 4. Modo Análisis (Prioridad BAJA)
- [ ] Vista con evaluación de posición
- [ ] Flechas de movimiento recomendado
- [ ] Variantes alternativas mostradas
- [ ] Integración con Chess.com para comparativa

**Impacto:** Herramienta educativa

---

## 🌟 Visión a Mediano Plazo (v2.5 - 3 meses)

### 1. Integración Chess.com API (Prioridad MEDIA)
- [ ] Obtener perfiles públicos de jugadores
- [ ] Descargar históricos mensuales (PGN)
- [ ] Daily Puzzle integrado en menú
- [ ] Ranking de apertura

**Impacto:** Acceso a datos públicos de Chess.com

### 2. Base de Datos de Partidas (Prioridad MEDIA)
- [ ] Almacenar partidas locales en SQLite
- [ ] Estadísticas: victorias/derrotas, tiempo promedio
- [ ] Historial de oponentes (si LAN)
- [ ] Búsqueda de posiciones dentro del DB

**Impacto:** Seguimiento de progreso a largo plazo

### 3. Temas Personalizables (Prioridad BAJA)
- [ ] Múltiples paletas de colores
- [ ] Tablero con texturas (madera, mármol, etc.)
- [ ] Sets de piezas alternativos
- [ ] Guardado de preferencias en JSON

**Impacto:** Customización visual

### 4. Modos Adicionales de Juego (Prioridad BAJA)
- [ ] Variantes de ajedrez: Fischer Random (Chess960)
- [ ] Blitz/Rápido con incremento de tiempo
- [ ] Modo torneo (round-robin)
- [ ] Partidas contra usuario remoto (cliente pesado)

**Impacto:** Variedad de modalidades

---

## 🚀 Visión a Largo Plazo (v3.0 - 6 meses)

### 1. Servidor Multiplayer en Línea (Prioridad BAJA)
- [ ] Backend Flask/FastAPI para partidas remotas
- [ ] Autenticación de usuarios
- [ ] Rating system (ELO)
- [ ] Chat y notificaciones

**Impacto:** Competencia global

### 2. Motor de IA Propio (Prioridad BAJA)
- [ ] Entrenamiento de red neuronal con python-chess
- [ ] Evaluador de posición basado en ML
- [ ] Búsqueda MCTS (Monte Carlo Tree Search)
- [ ] Comparativa con Stockfish

**Impacto:** Control total de algoritmo de IA

### 3. Aplicación Móvil (Prioridad MUY BAJA)
- [ ] Puerto a Kivy para Android/iOS
- [ ] Sincronización con versión escritorio
- [ ] Notificaciones push de movimientos

**Impacto:** Jugar desde cualquier dispositivo

### 4. Documentación Académica (Prioridad BAJA)
- [ ] Artículos sobre algoritmos (Minimax, Alpha-Beta)
- [ ] Tutoriales de ajedrez para principiantes
- [ ] Análisis de partidas famosas

**Impacto:** Valor educativo

---

## 📋 Backlog Técnico No Priorizado

### Mejoras de Rendimiento
- [ ] Caching de posiciones evaluadas
- [ ] Multithreading para búsqueda IA
- [ ] Optimización de dibujado (batch rendering)
- [ ] Profiling y benchmarking

### Robustez
- [ ] Manejo de excepciones mejorado
- [ ] Retry automático en LAN
- [ ] Logging detallado a archivo
- [ ] Tests unitarios + integración

### Distribución
- [ ] Compilar a ejecutable (PyInstaller)
- [ ] Instalador Windows (.msi)
- [ ] Paquete Snap/Flatpak para Linux
- [ ] DMG para macOS

### Accesibilidad
- [ ] Soporte para lectores de pantalla
- [ ] Modo alto contraste
- [ ] Teclado-only navigation
- [ ] Múltiples idiomas (i18n)

---

## 🔄 Ciclo de Desarrollo Actual

### Rama: `UI_LAN` (Actual)
- Menú jerárquico funcional
- LAN con protocolo estable
- Sombras RPG completamente implementado
- Documentación sincronizada

### Próxima Rama: `features/IA-minimax`
- Implementar Minimax + Alpha-Beta
- Tests de rendimiento vs Stockfish
- Niveles de dificultad expandidos

### Rama de Estabilidad: `main`
- Releases de versiones estables
- Actualmente: v2.0
- Proxima: v2.1 (cuando Minimax esté listo)

---

## 📈 Métricas de Progreso

| Aspecto | v1.0 | v2.0 | v2.1 (Planeado) |
|---|---|---|---|
| Modos de Juego | 3 | 5 | 7 |
| Líneas de Código | 2000 | 3500 | 4500 |
| Tests Automatizados | 0 | 0 | 20+ |
| Documentación | Básica | Completa | Con ejemplos |
| Rendimiento IA | N/A | Stockfish | Minimax+ |

---

## 🎯 Criterios de Éxito v2.1

- ✅ Minimax + Alpha-Beta en producción
- ✅ 5+ niveles de dificultad (Muy Fácil ~ Imposible)
- ✅ PGN guardar/cargar funcional
- ✅ Tests unitarios de IA
- ✅ Documentación de algoritmo

---

## 🗺️ Dependencias Entre Features

```
v2.0 (Actual)
│
├─→ v2.1: IA Minimax
│   └─→ v2.2: Análisis de posición
│       └─→ v2.5: Chess.com integración
│
├─→ v2.1: PGN guardar/cargar
│   └─→ v2.2: Base de datos
│       └─→ v2.5: Estadísticas avanzadas
│
└─→ v2.1: Temas personalizables
    └─→ v2.5: Múltiples sets de piezas
```

---

## 📞 Contacto y Contribuciones

**Proyecto:** Ajedrez (Pygame)  
**Owner:** U-ULabs  
**Repositorio:** Ajedrez (Rama: UI_LAN)  
**Licencia:** Educativo (2025)

**Cómo contribuir:**
1. Fork del repositorio
2. Crear rama feature (`git checkout -b features/mi-feature`)
3. Commit de cambios
4. Pull Request con descripción detallada

---

## 📝 Notas Importantes

### Sobre pygame-ce
- Se usa **pygame-ce (Community Edition)** 2.5.6 para compatibilidad con Python 3.14+
- La versión oficial de pygame aún no soporta Python 3.14
- pygame-ce mantiene compatibilidad total con el código existente

### Sobre Sombras
- Modo RPG completamente independiente de clásico
- No requiere Stockfish (IA tactica propia)
- Puede extenderse a otros juegos RPG

### Sobre LAN
- Protocolo JSON simple y extensible
- Futuro: WebSocket para Web version
- Descubrimiento UDP en LAN local (broadcast 255.255.255.255:8888)

---

## 🎉 Logros Alcanzados en v2.0

- ✅ Arquitectura modular limpia (ajedrez_clasico/ + ajedrez_sombras/)
- ✅ 5 modos jugables (4 clásico + 1 Sombras)
- ✅ Menú jerárquico intuitivo
- ✅ LAN multiplayer funcional
- ✅ Documentación profesional
- ✅ Código comentado y mantenible
- ✅ Import chain verificado y optimizado
- ✅ Cero errores de ejecución

**Estado Final: PRODUCCIÓN LISTA** ✅
