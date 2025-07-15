from rest_framework.views import APIView, status
from api.serializers import AlumnoSerializer
from rest_framework.response import Response
from api.models import Alumno
from django.contrib.auth.models import User
# Recordemos que tenemos 2 verbos HTTP muy famosos: GET y POST que se usan en una navegación normal.
# PERO en las APIs necesitamos manejar más que estos 2 verbos. Estos son lo que usaremos:
# 1. GET -> solo para obtener información (porque lleva parámetros visibles).
# 2. POST -> para insertar datos. También lo podemos usar para hacer login().
# 3. PUT -> para actualizar datos. Es similar a POST.
# 4. DELETE -> para eliminar.

class AlumnoAPI(APIView):
    
    def get(self, request):
        alumnos = Alumno.objects.all()
        # Con esta simple línea estamos transformando la lista de objetos de alumnos que vienen desde la BD
        # al tipo JSON que el navegador puede entender.
        datosSerializados = AlumnoSerializer(alumnos, many=True)
        return Response(datosSerializados.data)
    
    # La idea de post es que me envían datos para que aquí los inserte en la base de datos.
    # En este ejemplo, tenemos que lograr insertar un registro en la tabla Alumno.
    # Para "recoger" la información que viene en el POST y no tener que estar pasando uno por uno los
    # valores a los atributos del modelo, simplemente usaremos el Serializer
    #datosSerializados = AlumnoSerializer(data = request.data)
    def post(self, request):
        try:
            # No podremos usar el Serializer porque necesitamos manipular algunos datos después de crear un User.
            # Vamos a Serializar nosotros mismos la información que viene como un JSON.
            # PASO 1: creamos una copia de la información en una variable
            data = request.data.copy()
            # PASO 2: extraemos la información desde la copia que hicimos. Como request.data es un diccionario, para
            # extraer la información invocamos al método pop() y le pasamos por parámetro el valor a sacar.
            nombre = data.pop("nombre")
            apellido = data.pop("apellido")
            fecha_nacimiento = data.pop("fecha_nacimiento")

            # Recordemos que si estamos creando un Alumno, debería crearse un User en la BD.
            # El username será la primera letra del nombre + el apellido del alumno.
            username = f'{nombre[0]}{apellido}'
            password = "1234"
            email = username + '@correo.cl'
            
            # PASO 3: creamos un USER con esta información
            # Usemos el método create_user para que él se encargue de encriptar la contraseña.
            usuario = User.objects.create_user(username=username, password=password, email=email)
            usuario.save()

            alumno = Alumno()
            alumno.nombre = nombre
            alumno.apellido = apellido
            alumno.fecha_nacimiento = fecha_nacimiento
            # NO OLVIDAR!! La FK NO es el ID, sino el objeto completo que viene de la BD.
            # Por eso le pasamos el OBJETO usuario al user de alumno.
            alumno.user = usuario
            alumno.save()

            # Respondemos con los mismos que nos llegaron y añadimos el estado de la respuesta.
            # Como en este punto ya verificamos que todo venía OK y la inserción a la BD ya ocurrió,
            # devolver un estado 201 -> OK, se creó algo.
            return Response("OK", status=status.HTTP_201_CREATED)
        except:
            return Response("ERROR", status=status.HTTP_400_BAD_REQUEST)