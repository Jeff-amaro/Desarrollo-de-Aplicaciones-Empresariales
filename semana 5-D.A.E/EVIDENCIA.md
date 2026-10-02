# Evidencia del laboratorio 5 - Django Admin y modelos

Registro de la verificación de cada paso del procedimiento. El proyecto vive en
la carpeta `semana 5-D.A.E` de la rama `semana-5`.

## Entorno

| Elemento | Valor |
|---|---|
| Python | 3.12.10 |
| Django | 6.1.1 |
| Pillow | 12.3.0 |
| Base de datos | SQLite (`db.sqlite3`) |
| Superusuario | `admin` (creado con `createsuperuser`) |
| Usuario editor | `editor` / grupo `editores` |

## Estructura del proyecto

```
semana 5-D.A.E/
├── config/
│   ├── settings.py                 # Sin credenciales escritas a mano
│   └── urls.py                     # admin/ + movies
├── movies/
│   ├── admin.py                    # ModelAdmin, inline y readonly_fields
│   ├── management/commands/
│   │   ├── seed_movies.py          # Datos de prueba
│   │   └── setup_editor_permissions.py
│   ├── migrations/0001_initial.py
│   ├── models.py                   # Movie, Genre, Person, Rating
│   ├── templates/movies/           # recommendations, detail, search, base
│   ├── tests.py                    # 25 pruebas
│   ├── urls.py
│   └── views.py
├── .env.example
├── requirements.txt
└── setup.cfg                       # Reglas de pycodestyle
```

## Comandos de verificación

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m pycodestyle
```

Resultado: `check` sin incidencias, sin migraciones pendientes, 25 pruebas OK,
pycodestyle sin avisos (límite de 100 caracteres, migraciones excluidas).

## Paso 1. Proyecto y aplicación

Proyecto `config` generado con `django-admin startproject`, aplicación `movies`
declarada en `INSTALLED_APPS`, Pillow instalado para el campo de imagen
`Movie.poster` y `python-dotenv` para leer la configuración del archivo `.env`.

`settings.py` no tiene secretos escritos a mano: `SECRET_KEY` se lee de
`DJANGO_SECRET_KEY` y, si falta, se genera una vez y se guarda en `.secret_key`
(ignorado por git).

## Paso 2. Modelos

| Modelo | Campos principales | Relaciones |
|---|---|---|
| `Movie` | `title`, `synopsis`, `release_year`, `duration_minutes`, `poster` | M2M `genres`, M2M `directors`, M2M `actors` |
| `Genre` | `name`, `description` | muchos a muchos con `Movie` |
| `Person` | `first_name`, `last_name`, `birth_date` |actor y director |
| `Rating` | `score` (1-10), `comment` | FK a `Movie` y a `Person` |

Los cuatro modelos tienen `Meta` con `ordering` y `verbose_name`, y su `__str__`.
`Rating` incluye un `UniqueConstraint` que impide duplicar la valoración de una
misma persona en la misma película.

## Paso 3. Migraciones

`makemigrations movies` generó `0001_initial.py` con los cuatro modelos, el
índice de título y la restricción de unicidad. `migrate` aplicó correctamente
`movies.0001_initial`. El superusuario `admin` se creó con `createsuperuser`.

## Pasos 4 y 5. Registro y personalización del panel

Al registrar los cuatro modelos aparecen en el panel las operaciones de alta,
cambio, borrado y consulta, sin escribir ninguna vista.

`MovieAdmin` quedó con:

```python
list_display = ('title', 'release_year', 'genre_list', 'average_rating')
list_filter = ('genres', 'release_year')
search_fields = ('title', 'synopsis')
ordering = ('-release_year', 'title')
```

## Paso 6. Valoraciones dentro de la película

`RatingInline` (TabularInline) muestra las valoraciones como un bloque de
líneas dentro del formulario de la película, con `person`, `score` y `comment`,
de modo que se dan de alta sin salir del registro padre.

## Paso 7. Campos de auditoría en solo lectura

`readonly_fields = ('created_at', 'updated_at')` dentro de un `fieldsets`
llamado `Audit`. El panel muestra los valores y ya no permite editarlos; ambos
campos se rellenan solos con `auto_now_add` y `auto_now`.

## Paso 8. Datos de prueba

Cargados con `python manage.py seed_movies` (idempotente):

- 4 géneros: Drama, Science Fiction, Action, Comedy
- 7 personas
- 10 películas
- 14 valoraciones repartidas en las 10 películas

| Película | Año | Promedio | Géneros |
|---|---|---|---|
| The Matrix | 1999 | 9.5 | Action, Science Fiction |
| Arrival | 2016 | 8.5 | Drama, Science Fiction |
| Dune Part Two | 2024 | 9.5 | Action, Science Fiction |
| Inception | 2010 | 8.5 | Action, Science Fiction |
| Lost in Translation | 2003 | 8.0 | Comedy, Drama |
| Roma | 2018 | 9.0 | Drama |
| Coco | 2017 | 9.0 | Comedy, Drama |
| Bardo | 2022 | 7.0 | Comedy, Drama |
| The Lost City | 2022 | 8.0 | Action, Comedy |
| Sicario Dia del Soldado | 2018 | 8.0 | Action, Drama |

## Paso 9. Grupo «editores»

`python manage.py setup_editor_permissions` crea el grupo `editores` con los
permisos `add_movie` y `change_movie`, sin `delete_movie`, y el usuario `editor`
perteneciente al grupo.

| | Superusuario `admin` | Usuario `editor` |
|---|---|---|
| Movie | visible | visible |
| Genre | visible | oculto |
| Person | visible | oculto |
| Rating | visible | oculto |
| Añadir película | sí | sí |
| Cambiar película | sí | sí |
| Borrar película | sí | no (403) |

## Paso 10. Vista pública de recomendación

`movies.recommendations` calcula, por cada género, el promedio de
`ratings__score` y muestra las tres películas mejor valoradas. Los resultados
obtenidos:

```
Action           Dune Part Two (9.50), The Matrix (9.50), Inception (8.50)
Comedy           Coco (9.00), Lost in Translation (8.00), The Lost City (8.00)
Drama            Coco (9.00), Roma (9.00), Arrival (8.50)
Science Fiction  Dune Part Two (9.50), The Matrix (9.50), Arrival (8.50)
```

Complementan la vista el detalle de película (`/movies/<pk>/`) y una búsqueda
por título, año o género (`/movies/search/?q=...`).

El contraste pedido en el punto 11: el panel ofrece alta, edición y borrado con
filtros y búsqueda, pero no agrupa ni promedia valoraciones ni calcula rankings.
Para eso hace falta una vista propia, que es lo que hace
`movies.recommendations`.

## Paso 11. Capturas pendientes de tomar en el panel

Para completar el entregable faltan las capturas del entorno gráfico:

1. Panel con el registro simple de los cuatro modelos (paso 4).
2. Panel con `list_display`, `list_filter` y `search_fields` (paso 5).
3. Formulario de película con el bloque de valoraciones (paso 6).
4. Formulario con los campos de auditoría en solo lectura (paso 7).
5. Datos de prueba cargados (paso 8).
6. Comparación del índice del panel como superusuario y como `editor` (paso 9).
7. Vista pública de recomendaciones (paso 10).

## Reparto del trabajo

| Agente | Responsabilidad | Pasos |
|---|---|---|
| Django Architect | Estructura, modelos, `settings.py` sin credenciales | 1, 2 |
| Backend Developer | Modelos, `admin.py`, permisos, vista de recomendación | 2, 4, 5, 6, 7, 9, 10 |
| QA y Git Auditor | Migraciones, pruebas, datos de prueba, historial en `semana-5` | 3, 8, 11, 12 |

## Historial de commits (rama `semana-5`)

1. `chore: setup django project and register movies app`
2. `feat(movies): define Movie, Genre, Person, and Rating models`
3. `feat(movies): generate and apply initial database migrations`
4. `feat(admin): register models and customize ModelAdmin layout`
5. `feat(admin): add rating inline form and set audit fields read-only`
6. `feat(auth): configure editors group and user permissions`
7. `feat(movies): implement public recommendation view`
8. `test: verify test data and prepare execution evidence`
