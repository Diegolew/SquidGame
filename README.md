<h1 align="center" style="font-size: 3em;">🦑 SQUID GAME DETECTOR 🦑</h1>

**¡Bienvenido a Squid Game Detector!** Un proyecto inspirado en el famoso juego "Luz roja, luz verde" de la serie Squid Game... pero llevado al mundo de la visión por computadora. 🎯

**Creado por:** Diego Lewensztain

## 📚 ¿Qué es este proyecto?

Con ayuda de **inteligencia artificial**, **MediaPipe** y **OpenCV**, hemos desarrollado un sistema interactivo que:

- **Detecta movimientos humanos** en tiempo real usando tu cámara web
- **"Elimina jugadores"** que se mueven cuando no deberían (¡igual que en el juego!)
- **Recrea la experiencia** de una de las pruebas más icónicas de Squid Game
- Usa tecnologías accesibles para que cualquiera pueda probarlo en su computadora 🚀

## 🛠️ Tecnologías utilizadas

- **Python 3.11** - Lenguaje de programación principal
- **MediaPipe** - Para detección de postura corporal
- **OpenCV** - Procesamiento de video en tiempo real
- **Numpy** - Cálculos matemáticos rápidos

## 👀 ¿Por qué es interesante este proyecto?

- **No requiere hardware especial** - Solo necesitas tu cámara web integrada 🎥
- **Código educativo** - Perfecto para aprender visión por computadora
- **Sistema de detección preciso** - Usa múltiples puntos clave del cuerpo
- **Rendimiento optimizado** - Funciona en tiempo real incluso en hardware modesto
- **Divertido y competitivo** - Ideal para retos con amigos

## 🎮 ¿Cómo funciona el juego?

El sistema sigue este flujo:

1. **Detección inicial**:
   - Usa MediaPipe para identificar personas frente a la cámara
   - Asigna un ID único a cada jugador (hasta 3 máximo)

2. **Fase "Luz verde"**:
   - Los jugadores pueden moverse libremente
   - El sistema registra sus posiciones iniciales

3. **Fase "Luz roja"**:
   - Monitorea micromovimientos usando puntos clave corporales
   - Compara posiciones actuales con históricos
   - Si detecta movimiento por encima del umbral (`UMBRAL_MOVIMIENTO`), penaliza al jugador

4. **Visualización**:
   - Muestra esqueletos de los jugadores (verdes = seguros, rojos = penalizados)
   - Barra superior con estado del juego y jugadores eliminados

## ⚙️ Configuración técnica clave

El código utiliza varios parámetros ajustables:

```python
# Parámetros principales
UMBRAL_MOVIMIENTO = 0.01  # Sensibilidad al movimiento
MAX_JUGADORES = 3         # Límite de jugadores
MAX_HISTORICO = 5         # Frames almacenados para comparación