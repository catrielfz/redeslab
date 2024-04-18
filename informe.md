# Informe Laboratorio 2 Redes y Sistemas Distribuidos


## Estructura del Servidor

El servidor está compuesto por dos clases Server y Connection:

- La primera define su constructor con ****init****, el cual recibe una
direccion, un puerto y un directorio para luego crear el socket a utilizar,
añadiendole dichos parametros. A su vez, tiene un metodo **serve** el cual se
encarga de establecer las conexiones y llamar al metodo **handle** de la
segunda clase.

- La clase Connection define su propio constructor y metodos para satisfacer
los pedidos del cliente durante estas conexiones.

## Decisiones de Diseno

## General

En **conection.py**, el metodo `handle` realiza la llamada a `parser` para
poder interpretar los datos recibidos en el `buffer`. De manera que en el
`parser` separamos en distintos `comandos` lo que haya recibido el `buffer`
para que al final el metodo `handle` los ejecute según sea el caso.

Para algunos de estos métodos utilizamos un manejo de errores asegurandonos que
siempre se cumplan las precondiciones de cada uno.

## Especifico

- El Atributo `connected` es un booleano que identifica si la conexión está
activa.

- El Atributo `buffer` es un string en el cual se guarda los pedidos a eventos
o cualquier otro pedido erroneo.

- Metodo `parser`: Recibe datos por el buffer hasta encontrar un EOL, luego
toma el primer comando del buffer y lo retorna para que handle lo ejecute.

- Metodo `handle`: Llama al parser y segun el mensaje que éste retorne,
interpretamos que evento se va a ejecutar teniendo en cuenta los posibles
errores.

- Pedido `get_file_listing`: este comando muestra los archivos existentes
dentro del directorio del servidor.

- Pedido `get_metadata`: Este comando muestra la cantidad de bytes del archivo
que se especifique. Debe existir el archivo, de no ser asi arroja un OSError
avisando que no se puede acceder a el.

- Pedido `get_slice`: Devuelve una porcion del archivo solicitado en formato
b64code. Para esto se verifica que pueda abrir el archivo, que los parametros
offset y size sean de tipo int y que offset+size < file_size.

- Pedido `quit`: Cancela la conexion establecida entre el cliente y el
servidor. Primero manda mensaje de "0 OK" y luego finaliza la conexión.

## Dificultades

- Entender el proceso para probar el código y trabajar con las respectivas
excepciones que pueden aparecer usando try-except (por ejemplo: ValueError,
OSError, FileNotFoundError, entre otras).

- Comprender el funcionamiento del socket, asi como también el comportamiendo
del cliente y el servidor cuando se comunican a traves de éste.

- Manejo de los tests otorgados por la catedra para fortalecer la robustez del
servidor.

- Funciones y comportamientos especificos de Python.

- En el test multiple_command devuelve un warning que no sabriamos el motivo, este
se debe a la linea `c.close`. Comentandolo funcionan todos los test.

## Preguntas

1. ¿Qué estrategias existen para poder implementar este mismo servidor pero con
capacidad de atender múltiples clientes simultáneamente? Investigue y responda
brevemente qué cambios serían necesario en el diseño del código.

    - Threads:
    El server se encarga de crear distintos threads por cada cliente que se
    conecte, lo que permitiria la concurrencia. Cada thread tendra su propio
    handle para poder realizar todos los pedidos del cliente. Como buena
    practica se pudiera limitar la cantidad maxima de bytes que reciben los
    clientes como medida para no sobresaturar el server.

    - Selects:
    No seria posible la concurrencia como tal, sin embargo, es una opcion
    viable ya que es mas facil de implementar que los threads. La idea seria
    bloquear todas las conexiones y chequearlas hasta tener un evento completo.
    Seleccionar esta conexion y atender el pedido que se recibio. Al terminar
    ese pedido bloquea de nuevo la conexion y repite el chequeo.

2. Pruebe ejecutar el servidor en una máquina del laboratorio, mientras utiliza
el cliente desde otra, hacia la ip de la máquina servidor. ¿Qué diferencia hay
si se corre el servidor desde la IP “localhost”, “127.0.0.1” o la ip “0.0.0.0”?

    - Respuesta:
    127.0.0.1 es la dirección del protocolo de Internet de bucle (IP)
    también conocida como `localhost` por lo que no hay ninguna diferencia
    entre conectarnos a 127.0.0.1 o localhost.
    Por otro lado 0.0.0.0 hace referencia a cualquier direccion de la maquina local,
    es decir si ejecutamos el servidor en 0.0.0.0 este sera accesible desde cualquier
    direccion IP.
