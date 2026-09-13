# The Legend Of The Princess

## Sistema de Cofre y Arco
Interacción y Recompensa: Se implemento la probabilidad de que se genere un cofre (30% de probabilidad) cada vez que se entre a una room. Al acercarse, se abre el cofre y al presionar enter se activa player.has_bow = True y se equipa invocando player.bow = Bow().
Generación aleatoria: El cofre se genera en una posición libre aleatoria de la sala con su respectiva probabilidad, asegurando que no se superponga con otros objetos.
Mecánica de disparo y Patrón Factory:
Se creó la clase Bow con el método fire(player).
Se implementó la clase estática ArrowFactory. Al invocar fire(), el arco llama al Factory, el cual calcula la rotación, invierte la textura según hacia dónde mira el jugador y devuelve un objeto de la clase Projectile.
Todo respeta un cooldown de 1 segundo controlado por el dt.

## Habitación del Jefe y Comportamiento
Acceso a la sala: En la función que hace la transición de salas, se añadió un condicional: si el jugador ya tiene el arco, hay una probabilidad (40%) de instanciar un objeto de clase BossRoom en lugar de un Room normal.
Estructura de la habitación: Esta clase hereda de Room pero anula la generación de entidades y objetos (quedando completamente vacía). Luego, lee la dirección de entrada para colocar al Boss en el extremo opuesto.
Puntos de vida y Patrón de Combate:
La clase Boss inicia con 20 hp.
Posee un temporizador que instancia objetos de la nueva clase Fireball.
Cada Fireball calcula la trayectoria lenta y exacta hacia las coordenadas (x, y) donde estaba parado el jugador al momento de dispararse.
Mecánica de Inmunidad / Vulnerabilidad:
El método damage() (para la espada) ignora el daño a menos que la variable self.vulnerable sea verdadera.
Al chocar una flecha con el jefe, se dispara su vulnerabilidad por 2 segundos, la IA del jefe detiene el disparo de fuego y el movimiento, permitiendo dañarlo.
Daño al jugador: En el bucle de actualización (update) de la sala, se evalúan las colisiones,
Si el rectángulo de una Fireball choca con el del jugador, se aplica daño máximo.
Si el cuerpo del Boss choca con el jugador, se le restan 2 puntos de vida (el equivalente a un corazón completo).
