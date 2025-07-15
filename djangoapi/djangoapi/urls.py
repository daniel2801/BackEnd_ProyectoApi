from django.contrib import admin
from django.urls import path
from api import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    # path("empleado/", v.empleado),
    # path("empleados/", v.empleadeichons),
    path("alumnos/", v.AlumnoAPI.as_view()), # como ahora estamos basados en clases y no en funciones,
    # necesitmos apuntar a la clase completa y llamar al método as_view()
]
