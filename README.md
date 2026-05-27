¿Cómo el hardware emulado se comunica con la nube usando el Token JWT?

El hardware emulado (sensor falso que hicimos con python) se comunica con la nube mediante 
peticiones http y le pide permiso al sistema obteniendo un token JWT desde el endpoint y cada vez que envía una lectura junto con ella manda ese token 
en el encabezado "Authorization: Bearer < TOKEN >" después el backend revisa el token, verifica si es que está autorizado y guarda la lectura en la base de datos.
