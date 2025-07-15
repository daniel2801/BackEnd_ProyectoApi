from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .models import Libro, Sucursal, Prestamo, Reserva, Ejemplar
from .serializers import LibroSerializer, SucursalSerializer, PrestamoSerializer, ReservaSerializer, EjemplarSerializer, UsuarioSerializer
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils import timezone

# Solo permite acceso a usuarios tipo admin
class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo == 'admin'

# Permite acceso a bibliotecarios y admin
class EsBibliotecarioOAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo in ['bibliotecario', 'admin']

# Mensaje personalizado si no hay datos
class ListaAPIViewConMensajeVacio(generics.ListAPIView):
    mensaje_vacio = {'Alerta': 'No existen datos.'}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response(self.mensaje_vacio)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
# Registrar usuarios (admin)
class VistaRegistro(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [EsAdmin]

# Ver y actualizar el perfil de Usuario
class UsuarioPerfilVistaAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [EsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        usuario = self.request.user
        # (bibliotecario o admin) ver/editar cualquier usuario
        if hasattr(usuario, 'tipo') and usuario.tipo in ['bibliotecario', 'admin']:
            usuario_id = self.request.query_params.get('usuario_id')
            if usuario_id:
                from .models import Usuario
                return Usuario.objects.get(pk=usuario_id)
        return self.request.user

# Ver el historial de préstamos del usuario
class UsuarioHistorialPrestamosVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = PrestamoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'tipo') and usuario.tipo in ['bibliotecario', 'admin']:
            usuario_id = self.request.query_params.get('usuario_id')
            if usuario_id:
                from .models import Usuario
                return Prestamo.objects.filter(usuario_id=usuario_id).order_by('-fecha_prestamo')
        return Prestamo.objects.filter(usuario=usuario).order_by('-fecha_prestamo')

# Ver las reservas del usuario autenticado
class UsuarioMisReservasVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'tipo') and usuario.tipo in ['bibliotecario', 'admin']:
            usuario_id = self.request.query_params.get('usuario_id')
            if usuario_id:
                from .models import Usuario
                return Reserva.objects.filter(usuario_id=usuario_id).order_by('-fecha_reserva')
        return Reserva.objects.filter(usuario=usuario).order_by('-fecha_reserva')
    
# listar y crear libros
class LibroListaCrearVistaAPI(generics.ListCreateAPIView):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [EsBibliotecarioOAdmin()]
        return [permissions.IsAuthenticated()]

# Listar, actualizar o eliminar un libro
class LibroObtenerActualizarEliminarVistaAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [EsBibliotecarioOAdmin()]
        if self.request.method == 'DELETE':
            return [EsAdmin()]
        return [permissions.IsAuthenticated()]

# Buscar libros por filtros
class LibroBuscarVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = LibroSerializer

    def get_queryset(self):
        queryset = Libro.objects.all()
        titulo = self.request.query_params.get('titulo')
        autor = self.request.query_params.get('autor')
        isbn = self.request.query_params.get('isbn')
        genero = self.request.query_params.get('genero')
        ano_publicacion = self.request.query_params.get('ano_publicacion')
        disponible = self.request.query_params.get('disponible')
        sucursal = self.request.query_params.get('sucursal')
        # Filtro
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)
        if autor:
            queryset = queryset.filter(autor__icontains=autor)
        if isbn:
            queryset = queryset.filter(isbn__icontains=isbn)
        if genero:
            queryset = queryset.filter(genero__icontains=genero)
        if ano_publicacion:
            queryset = queryset.filter(ano_publicacion=ano_publicacion)
        if disponible == 'true':
            queryset = queryset.filter(ejemplares__estado='disponible').distinct()
        if sucursal:
            queryset = queryset.filter(ejemplares__sucursal__id=sucursal).distinct()
        return queryset

# Consultar la disponibilidad de ejemplares de un libro
class LibroDisponibilidadVistaAPI(generics.RetrieveAPIView):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ejemplares = instance.ejemplares.all()
        total = ejemplares.count()
        disponibles = ejemplares.filter(estado='disponible').count()
        prestados = ejemplares.filter(estado='prestado').count()
        mantenimiento = ejemplares.filter(estado='mantenimiento').count()

        # Por sucursales
        sucursales = {}
        for ejemplar in ejemplares:
            nombre_sucursal = ejemplar.sucursal.nombre
            if nombre_sucursal not in sucursales:
                sucursales[nombre_sucursal] = {"disponibles": 0, "prestados": 0, "mantenimiento": 0}
            if ejemplar.estado == "disponible":
                sucursales[nombre_sucursal]["disponibles"] += 1
            elif ejemplar.estado == "prestado":
                sucursales[nombre_sucursal]["prestados"] += 1
            elif ejemplar.estado == "mantenimiento":
                sucursales[nombre_sucursal]["mantenimiento"] += 1
            else:
                pass

        por_sucursal = [
            {
                "sucursal": nombre,
                "disponibles": datos["disponibles"],
                "prestados": datos["prestados"],
                "mantenimiento": datos["mantenimiento"]
            }
            for nombre, datos in sucursales.items()
        ]

        # Reservas pendientes
        reservas_pendientes = instance.reservas.filter(estado='en cola').count()

        return Response({
            "total_ejemplares": total,
            "disponibles": disponibles,
            "prestados": prestados,
            "mantenimiento": mantenimiento,
            "por_sucursal": por_sucursal,
            "reservas_pendientes": reservas_pendientes
        })

# Listar y crear préstamos
class PrestamoListaCrearVistaAPI(ListaAPIViewConMensajeVacio, generics.CreateAPIView):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [EsBibliotecarioOAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'tipo') and usuario.tipo in ['bibliotecario', 'admin']:
            return Prestamo.objects.all()
        return Prestamo.objects.filter(usuario=usuario)

# Ver Préstamos
class PrestamoObtenerVistaAPI(generics.RetrieveAPIView):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer

# Devolver un préstamo
class PrestamoDevolverVistaAPI(generics.UpdateAPIView):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [EsBibliotecarioOAdmin()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        fecha_real_devolucion = timezone.now().date()
        fecha_entrega_estipulada = instance.fecha_devolucion

        instance.estado = 'devuelto'
        instance.fecha_devolucion = fecha_real_devolucion

        # Cálculo de multa
        if fecha_real_devolucion > fecha_entrega_estipulada:
            dias_retraso = (fecha_real_devolucion - fecha_entrega_estipulada).days
            instance.multa = dias_retraso * 1000  # 1000 por dia de retraso
        else:
            instance.multa = 0

        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Ver préstamos activos del usuario
class PrestamosActivosVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'tipo') and usuario.tipo in ['bibliotecario', 'admin']:
            return Prestamo.objects.filter(estado='activo')
        return Prestamo.objects.filter(usuario=usuario, estado='activo')

# Ver préstamos vencidos del usuario
class PrestamosVencidosVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        usuario = self.request.user
        if hasattr(usuario, 'tipo') and usuario.tipo in ['bibliotecario', 'admin']:
            return Prestamo.objects.filter(estado='vencido')
        return Prestamo.objects.filter(usuario=usuario, estado='vencido')
    
# listar y crear reservas
class ReservaListaCrearVistaAPI(ListaAPIViewConMensajeVacio, generics.CreateAPIView):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [EsBibliotecarioOAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        libro = serializer.validated_data['libro']
        # Calcular posicion en cola
        posicion = Reserva.objects.filter(libro=libro, estado='en cola').count() + 1
        serializer.save(usuario=self.request.user, posicion_cola=posicion)

# Eliminar una reserva
class ReservaEliminarVistaAPI(generics.DestroyAPIView):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [EsBibliotecarioOAdmin()]
        return [permissions.IsAuthenticated()]

# Cancelar una reserva
class ReservaCancelarVistaAPI(generics.UpdateAPIView):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [EsBibliotecarioOAdmin()]
        return [permissions.IsAuthenticated()]
    #cola
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        libro = instance.libro
        posicion_cancelada = instance.posicion_cola
        instance.estado = 'cancelada'
        instance.save()
        # Avanzar la cola
        reservas = Reserva.objects.filter(libro=libro, estado='en cola', posicion_cola__gt=posicion_cancelada)
        for reserva in reservas:
            reserva.posicion_cola -= 1
            reserva.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Ver la cola de reservas de un libro
class ReservaColaVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = ReservaSerializer

    def get_queryset(self):
        libro_id = self.kwargs['libro_id']
        return Reserva.objects.filter(libro_id=libro_id).order_by('posicion_cola')

# Listar y crear sucursales
class SucursalListaCrearVistaAPI(generics.ListCreateAPIView):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [EsAdmin()]
        return [permissions.IsAuthenticated()]

# Obtener una sucursal
class SucursalObtenerVistaAPI(generics.RetrieveAPIView):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer

# Ver el inventario de una sucursal
class SucursalInventarioVistaAPI(ListaAPIViewConMensajeVacio):
    serializer_class = EjemplarSerializer

    def get_queryset(self):
        sucursal_id = self.kwargs['pk']
        return Ejemplar.objects.filter(sucursal_id=sucursal_id)

# Transferir un ejemplar
class EjemplarTransferirVistaAPI(generics.UpdateAPIView):
    queryset = Ejemplar.objects.all()
    serializer_class = EjemplarSerializer
    permission_classes = [EsAdmin]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [EsAdmin()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        nueva_sucursal_id = request.data.get('sucursal_id')
        if not nueva_sucursal_id:
            return Response({'error': 'Debes proporcionar el ID de la nueva sucursal.'}, status=400)
        try:
            nueva_sucursal = Sucursal.objects.get(pk=nueva_sucursal_id)
        except Sucursal.DoesNotExist:
            return Response({'error': 'Sucursal no encontrada.'}, status=404)
        instance.sucursal = nueva_sucursal
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Reporte de libros más populares
class ReporteLibrosPopularesVistaAPI(ListaAPIViewConMensajeVacio):
    permission_classes = [EsBibliotecarioOAdmin]
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        # Más prestados
        datos = (
            Prestamo.objects.values('ejemplar__libro__titulo')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )
        return datos

    def list(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        if not queryset:
            return Response(self.mensaje_vacio)
        return Response(queryset)

# Reporte de usuarios con multas
class ReporteMorosidadVistaAPI(ListaAPIViewConMensajeVacio):
    permission_classes = [EsBibliotecarioOAdmin]
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        datos = (
            Prestamo.objects.filter(multa__gt=0)
            .values('usuario__username')
            .annotate(total_multa=Count('multa'))
        )
        return datos

    def list(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        if not queryset:
            return Response(self.mensaje_vacio)
        return Response(queryset)

# Reporte de estadísticas por sucursal
class ReporteEstadisticasSucursalVistaAPI(ListaAPIViewConMensajeVacio):
    permission_classes = [EsBibliotecarioOAdmin]
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        datos = (
            Prestamo.objects.values('ejemplar__sucursal__nombre')
            .annotate(total=Count('id'))
        )
        return datos

    def list(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        if not queryset:
            return Response(self.mensaje_vacio)
        return Response(queryset)