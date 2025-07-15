from rest_framework import serializers
from .models import Libro, Sucursal, Prestamo, Reserva, Ejemplar, Usuario
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db.models import Sum

# Serializador Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    nombre = serializers.CharField(source='first_name')
    apellido = serializers.CharField(source='last_name')
    prestamos_activos = serializers.SerializerMethodField()
    multas_pendientes = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'password', 'email', 'nombre', 'apellido', 'tipo',
            'prestamos_activos', 'multas_pendientes'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        nombre = validated_data.pop('first_name', None)
        apellido = validated_data.pop('last_name', None)
        if nombre:
            validated_data['first_name'] = nombre
        if apellido:
            validated_data['last_name'] = apellido
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_prestamos_activos(self, obj):
        return Prestamo.objects.filter(usuario=obj, estado='activo').count()

    def get_multas_pendientes(self, obj):
        # Suma multas de prestamos activos del usuario y devuelve como entero
        total = Prestamo.objects.filter(usuario=obj, estado='activo').aggregate(total=Sum('multa'))['total']
        return int(total) if total else 0

# Serializador Libro
class LibroSerializer(serializers.ModelSerializer):
    total_ejemplares = serializers.SerializerMethodField()
    ejemplares_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = '__all__'

    def get_total_ejemplares(self, obj):
        return obj.ejemplares.count()

    def get_ejemplares_disponibles(self, obj):
        return obj.ejemplares.filter(estado='disponible').count()
    
    def validate(self, data):
        # No puede eliminar libro si tiene prestamos activos
        if self.instance:
            prestamos_activos = Prestamo.objects.filter(
                ejemplar__libro=self.instance,
                estado='activo'
            )
            request = self.context.get('request')
            if request and request.method == 'DELETE' and prestamos_activos.exists():
                raise ValidationError('No se puede eliminar un libro con préstamos activos.')
        return data

# Serializador Sucursal
class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'

# Serializador Ejemplar
class EjemplarSerializer(serializers.ModelSerializer):
    libro = LibroSerializer(read_only=True)

    class Meta:
        model = Ejemplar
        fields = '__all__'

# Serializador Prestamo
class PrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestamo
        fields = '__all__'

    def validate(self, data):
        usuario = self.context['request'].user
        # Max 3 prestamos activos
        if Prestamo.objects.filter(usuario=usuario, estado='activo').count() >= 3:
            raise ValidationError('No puedes tener más de 3 préstamos activos.')
        # Max prestamo 14 días
        if data.get('fecha_devolucion'):
            delta = data['fecha_devolucion'] - timezone.now().date()
            if delta.days > 14:
                raise ValidationError('La duración máxima de un préstamo es de 14 días.')
        return data

# Serializador Reserva
class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'

    def validate(self, data):
        usuario = self.context['request'].user
        # No puede reservar si el usuario tiene multas
        if Prestamo.objects.filter(usuario=usuario, multa__gt=0, estado='activo').exists():
            raise ValidationError('No puedes reservar libros si tienes multas pendientes.')
        return data