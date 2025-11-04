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