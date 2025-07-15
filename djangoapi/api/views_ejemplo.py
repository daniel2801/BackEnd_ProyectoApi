from django.http import JsonResponse

def empleado(request):
    data = {
        "id": 1234,
        "nombre": "Benjamín",
        "apellido": "Campos",
        "email": "ignacio.pino@gmail.com",
        "salario": 950000
    }
    return JsonResponse(data)

def empleadeichons(request):
    data = [
            {
                "id": 1234,
                "nombre": "Benjamín",
                "apellido": "Campos",
                "email": "ignacio.pino@gmail.com",
                "salario": 950000
            },
            {
                "id": 1898,
                "nombre": "Daniel",
                "apellido": "Millaquén",
                "email": "ignacio.pino@gmail.com",
                "salario": 950000
            },
            {
                "id": 2222,
                "nombre": "Lucas",
                "apellido": "Ramírez",
                "email": "ignacio.pino@gmail.com",
                "salario": 950000
            }
        ]
    # Para permitir que se envíen listas directamente como respuesta, tenemos que agregar el parámetro safe en False
    return JsonResponse(data, safe=False)