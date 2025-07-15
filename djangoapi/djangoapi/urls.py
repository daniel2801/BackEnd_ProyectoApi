from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import api.views as v

urlpatterns = [
    # Autenticacion
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', v.VistaRegistro.as_view(), name='register'),

    # Libros
    path('libros/', v.LibroListaCrearVistaAPI.as_view()),
    path('libros/<int:pk>/', v.LibroObtenerActualizarEliminarVistaAPI.as_view()),
    path('libros/buscar/', v.LibroBuscarVistaAPI.as_view()),
    path('libros/<int:pk>/disponibilidad/', v.LibroDisponibilidadVistaAPI.as_view()),

    # Usuarios
    path('usuarios/perfil/', v.UsuarioPerfilVistaAPI.as_view()),
    path('usuarios/historial-prestamos/', v.UsuarioHistorialPrestamosVistaAPI.as_view()),
    path('usuarios/mis-reservas/', v.UsuarioMisReservasVistaAPI.as_view()),

    # Préstamos
    path('prestamos/', v.PrestamoListaCrearVistaAPI.as_view()),
    path('prestamos/<int:pk>/', v.PrestamoObtenerVistaAPI.as_view()),
    path('prestamos/<int:pk>/devolver/', v.PrestamoDevolverVistaAPI.as_view()),
    path('prestamos/activos/', v.PrestamosActivosVistaAPI.as_view()),
    path('prestamos/vencidos/', v.PrestamosVencidosVistaAPI.as_view()),

    # Reservas
    path('reservas/', v.ReservaListaCrearVistaAPI.as_view()),
    path('reservas/<int:pk>/', v.ReservaEliminarVistaAPI.as_view()),
    path('reservas/<int:pk>/cancelar/', v.ReservaCancelarVistaAPI.as_view()),
    path('reservas/cola/<int:libro_id>/', v.ReservaColaVistaAPI.as_view()),

    # Sucursales
    path('sucursales/', v.SucursalListaCrearVistaAPI.as_view()),
    path('sucursales/<int:pk>/', v.SucursalObtenerVistaAPI.as_view()),
    path('sucursales/<int:pk>/inventario/', v.SucursalInventarioVistaAPI.as_view()),
    path('ejemplares/<int:pk>/transferir/', v.EjemplarTransferirVistaAPI.as_view()),

    # Reportes
    path('reportes/populares/', v.ReporteLibrosPopularesVistaAPI.as_view()),
    path('reportes/morosidad/', v.ReporteMorosidadVistaAPI.as_view()),
    path('reportes/estadisticas-sucursal/', v.ReporteEstadisticasSucursalVistaAPI.as_view()),
]