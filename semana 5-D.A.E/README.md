# Semana 5 - Django Admin y Django Models

Laboratorio 5 del curso de Desarrollo de Aplicaciones Empresariales. El
proyecto implementa el panel de administración de Django sobre un catálogo de
películas, con sus géneros, personas y valoraciones, y una vista pública de
recomendación.

## Estructura

```
semana 5-D.A.E/
├── config/                  # Configuración del proyecto
│   ├── settings.py
│   └── urls.py
├── movies/                  # Aplicación de negocio
│   ├── admin.py             # Registro y personalización del panel
│   ├── management/commands/ # Comandos para datos de prueba y permisos
│   ├── migrations/
│   ├── models.py
│   ├── templates/movies/
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .env.example             # Plantilla de variables de entorno
├── manage.py
└── requirements.txt
```

## Requisitos

- Python 3.12 o superior
- Dependencias de `requirements.txt` (Django, Pillow y python-dotenv)

## Puesta en marcha

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
python manage.py makemigrations movies
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

El panel queda disponible en `http://127.0.0.1:8000/admin/`.

## Datos de prueba y permisos

```bash
python manage.py seed_movies
python manage.py setup_editor_permissions
```

Ambos comandos son idempotentes: se pueden volver a ejecutar sin duplicar
datos.

## Comandos de verificación

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Nota de seguridad

`settings.py` no contiene credenciales escritas a mano. La clave secreta se
lee de `DJANGO_SECRET_KEY` y, si no está definida, se genera una vez y se
guarda en `.secret_key`, archivo que está en `.gitignore`.
