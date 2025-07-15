from django.db import models
from django.contrib.auth import get_user_model
# El método get_user_model() me devuelve un objeto de la clase User que es creada y manejada por DJango.
User = get_user_model()

class Alumno(models.Model):

    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    fecha_nacimiento = models.DateField()
    # Como la relación de Alumno - User es de 1:1, entonces no vamos a usar models.ForeingField(), sino
    # que usaremos el método OneToOneField() y le pasamos User que es el objeto que creamos al principio.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "alumno"

class Profesor(models.Model):

    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    valor_hora = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "profesor"

class Asignatura(models.Model):

    nombre = models.CharField(max_length=40)
    cupos = models.IntegerField()

    class Meta:
        db_table = "asignatura"

class Notas(models.Model):

    nota = models.FloatField()
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)

    class Meta:
        db_table = "notas"