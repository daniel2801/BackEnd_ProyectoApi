from rest_framework import serializers
from api.models import Alumno

# Los serializadores nos ayudan a automatizar el proceso de convertir un modelo de la BD
# a datos tipo JSON. Y también al revés: de JSON a modelo de datos.
# Si hiciéramos esto manualmente nos tomaría hartas líneas de código.
# PERO, podemos crear una clase que herede de ModelSerializer y así automatizar el proceso.
class AlumnoSerializer(serializers.ModelSerializer):
    # Tenemos que crear una clase internta llamada Meta
    class Meta:
        # Aquí añadimos el atributo model con la clase que corresponda al model (no olvides importala)
        model = Alumno
        # En fields indicamos qué atributos queremos serializar. Si simplemente quieres que TODOS se
        # serialicen, entonces pone "__all__".
        fields = "__all__"