from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Tipos de usuario
class Usuario(AbstractUser):
    TIPOS = (
        ('regular', 'Usuario Regular'),
        ('bibliotecario', 'Bibliotecario'),
        ('admin', 'Administrador'),
    )
    tipo = models.CharField(max_length=15, choices=TIPOS, default='regular')
    # Los campos username, password, email, first_name, last_name ya están en el AbstractUser

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"

# Sucursal de la biblioteca
class Sucursal(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50) 
    telefono = models.CharField(max_length=15) 
    horario_atencion = models.CharField(max_length=50, blank=True, default="") 

    def __str__(self):
        return self.nombre

# Libro en el catálogo
class Libro(models.Model):
    titulo = models.CharField(max_length=200) 
    autor = models.CharField(max_length=100) 
    isbn = models.CharField(max_length=20, unique=True)  # ISBN único
    genero = models.CharField(max_length=50) 
    ano_publicacion = models.PositiveIntegerField() 
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.titulo} - {self.autor}"

# Ejemplar fisico de un libro
class Ejemplar(models.Model):
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('mantenimiento', 'En Mantenimiento'),
    )
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')  
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='ejemplares') 
    codigo_barras = models.CharField(max_length=30, unique=True) 
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')

    def __str__(self):
        return f"{self.libro.titulo} ({self.codigo_barras}) - {self.sucursal.nombre}"

# Préstamo de un ejemplar a usuario
class Prestamo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='prestamos')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos') 
    fecha_prestamo = models.DateField(auto_now_add=True) 
    fecha_devolucion = models.DateField(null=True, blank=True) 
    estado = models.CharField(max_length=20, default='activo')
    multa = models.DecimalField(max_digits=6, decimal_places=2, default=0) 

    def __str__(self):
        return f"{self.usuario.username} - {self.ejemplar.libro.titulo}"

# Reserva de un libro por usuario
class Reserva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas') 
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateTimeField(auto_now_add=True) 
    estado = models.CharField(max_length=20, default='en cola')  
    posicion_cola = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return f"{self.usuario.username} reserva {self.libro.titulo} (Posición: {self.posicion_cola})"

    @staticmethod
    def liberar_reservas_expiradas():
        """Libera reservas que llevan más de 2 días en cola."""
        expiradas = Reserva.objects.filter(estado='en cola', fecha_reserva__lt=timezone.now()-timezone.timedelta(days=2))
        for reserva in expiradas:
            reserva.estado = 'expirada'
            reserva.save()