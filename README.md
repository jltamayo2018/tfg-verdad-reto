# tfg-verdad-reto
El proyecto consiste en el desarrollo de una aplicación web para implementar y gestionar el juego "Verdad o Reto". Los propios jugadores serán quienes creen los contenidos y participen en las pruebas. Como técnica principal para el intercambio de enlaces se utilizará la generación y el escaneo de códigos QR.

20/09/2025

Creo el repositorio y lo clono en mi pc.
python -m venv entornoVirtual-VR -> para la creación del entorno virtual
.\entornoVirtual-VR\Scripts\activate -> para activarlo
pip install django pillow qrcode -> instalamos django y varias librerías. pillow sirve para manejo de errores, qrcode para generar los QR.
Creación del proyecto y la app principal
creado home, base, login y registro

22/09/2025

Completado el login, registro y logout.
Creado el dashboard, donde cada usuario podrá ver sus packs, crearlos, modificarlos, eliminarlos.
Creación de los modelos Pack y acción.

23/09/2025

Página de mis Packs ya muestra los packs y se pueden generar nuevos packs.
En cada pack se muestran las preguntas y retos del pack. Y permite crear, editar, desactivar y borrar las verdades/retos.
Enlaces a la página de verdad/reto de cada pack, donde se muestra una aleatorio cada vez.

25/09/25

Mejora de algunas funcionalidades y plantillas
Generación de QRs implementada

26/09/25

Botón de regeneración de enlaces
Mejoras en el base.html
Hoja de estilos css creada, aspecto visual neón implementado.

29/09/25

Mejoras visuales en la web.
No hay desbordamiento horizontal, está centrado.
Página "Mis packs" mejorada considerablemente, ya no aparece como una lista, los packs aparecen en cuadrados, 2 por fila.
Página de detalles del pack mejorada considerablemente, vistosa, acordeones...

30/09/25

Mejoras estéticas y funcionales en muchasde las páginas de la web

20/10/25

Despliegue

21/10/2025

Resolución de errores, redirecciones y otros

04/11/2025

Funcionalidad para dar accesos de editor de packs

11/11/25

COMIENZO PARA AÑADIR SESIONES VIDEOCONFERENCIA

pip install channels channels-redis
configuración del fichero settings.py para la configuración de canales

WSGI (Web Server Gateway Interface) es el estándar clásico que usa Django desde siempre. Diseñado para aplicaciones web sin tiempo real, donde cada petición HTTP empieza y termina de forma independiente.
ASGI (Asynchronous Server Gateway Interface) es la evolución moderna del WSGI. Soporta protocolos asíncronos, no solo HTTP

configuración del fichero asgi.py
creación de consumers.py
urls.py añadimos las salas de juego
views, las funciones necesarias
creamos room.html
creamos los modelos necesarios

12/11/25

Escribiendo directamente la url http://localhost:4000/rooms/create/<id_pck>>/ se crea la sala. El primer problema es que jitsi pide iniciar sesión con google o github y da error 403 (creo que por el incógnito)
meet.jit.si

16/11/2025

Botón para crear sala creado en la página de detalles del pack

17/11/2025

Se eliminan las salas de la base de datos cuando no se utilizan y caducan.

18/11/2025

Tratando de corregir los errores en la creación de la sala

15/12/2025

Cambios de estilos y retoques en el html
DB nueva en Neon, ya que en Render es temporal
Push al repo con todos los nuevos cambios de VIDEOROOMS
Settings actualizado para que funcionen los channels y ASGI
Cambios en el start command de Render para que haga el despliegue con daphne
Upstash para la REDIS_URL

08/01/2026

Recopilación de errores y cosas a mejorar

09/01/2026

Icono del 'ojo' añadido a los campos de contraseña en la página de registro