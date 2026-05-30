# AutoLog 🔧

**Registro de Mantenimiento Vehicular con DevSecOps**

Aplicación web para llevar el historial completo de mantenimiento de vehículos. Desarrollada en Python/Flask como evidencia académica de la materia **Seguridad Cloud**.

---

## Características

- Registro de múltiples vehículos por usuario
- Historial de servicios con fecha, kilometraje, costo y taller
- +14 tipos de servicio predefinidos
- Estadísticas de gasto por vehículo
- Búsqueda y filtrado de registros
- Autenticación segura con sesiones de servidor

## Medidas de Seguridad Implementadas

| Medida | Librería / Técnica |
|--------|-------------------|
| Hashing de contraseñas | Werkzeug `pbkdf2:sha256` |
| Sesiones seguras | Flask-Login + cookies HttpOnly / SameSite=Strict |
| Protección CSRF | Flask-WTF (token en cada formulario) |
| Consultas parametrizadas | SQLAlchemy ORM |
| Cabeceras HTTP seguras | Flask-Talisman + CSP estricta |
| Limitación de peticiones | Flask-Limiter (brute-force en /signin, /signup) |
| Prevención XSS | Autoescape Jinja2 |
| Variables de entorno | python-dotenv |

## Pipeline CI/CD (GitHub Actions)

Cada push a `main` ejecuta automáticamente:

1. **Gitleaks** — Escaneo de secretos en el repositorio
2. **pip-audit** — Análisis de dependencias vulnerables
3. **Bandit** — Análisis estático de seguridad del código Python
4. **pytest** — Pruebas unitarias con SQLite en memoria

## Stack Tecnológico

- **Backend:** Python 3.10, Flask 3.0
- **Base de datos:** MySQL (PythonAnywhere) / SQLite (pruebas)
- **ORM:** SQLAlchemy
- **Frontend:** HTML5, CSS3, Jinja2, JavaScript vanilla
- **Hospedaje:** PythonAnywhere (gratuito)
- **Monitoreo:** Better Stack (uptime + página de estado pública)
- **CI/CD:** GitHub Actions

## Estructura del Proyecto

```
autolog/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Modelos User, Vehicle, MaintenanceRecord
│   ├── auth/                # Blueprint de autenticación
│   ├── vehicles/            # Blueprint de vehículos y registros
│   └── main/                # Blueprint principal (index, dashboard, status)
├── templates/               # Plantillas Jinja2
├── static/                  # CSS y JavaScript
├── tests/                   # Pruebas unitarias pytest
├── .github/workflows/       # Pipeline GitHub Actions
├── wsgi.py                  # Entry point
├── requirements.txt
└── .env.example
```

## Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `/` | Página de inicio pública |
| `/signup` | Registro de usuario |
| `/signin` | Inicio de sesión |
| `/dashboard` | Panel del usuario (autenticado) |
| `/vehicles/new` | Agregar vehículo |
| `/vehicles/<id>/records` | Historial de un vehículo |
| `/status` | Health check para monitoreo externo |

## Monitoreo

El endpoint `/status` devuelve un JSON con el estado de la aplicación y la base de datos. Está conectado a **Better Stack** para monitoreo de disponibilidad 24/7 con alertas automáticas y página pública de estado.
