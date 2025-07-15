from django.contrib import admin
from .models import Usuario, Sucursal, Libro, Ejemplar, Prestamo, Reserva

admin.site.register(Usuario)
admin.site.register(Sucursal)
admin.site.register(Libro)
admin.site.register(Ejemplar)
admin.site.register(Prestamo)
admin.site.register(Reserva)