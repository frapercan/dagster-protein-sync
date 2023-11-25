# Gestión del Sistema de Información UniProt/PDB

## Descripción General

Este proyecto implementa un sistema para cargar y procesar datos de proteínas desde UniProt utilizando Python. El código se estructura alrededor de dos funciones principales, cada una representada como un "activo" (asset) en el contexto de Dagster, un marco de trabajo para la orquestación de datos.

## Dependencias

- **Python:** Lenguaje de programación utilizado.
- **Dagster:** Utilizado para la orquestación de datos y la definición de activos.
- **SQLAlchemy:** ORM para interactuar con bases de datos.
- **PostgreSQL:** Sistema de gestión de bases de datos donde se almacenan los datos.
- **Psycopg2:** Adaptador de base de datos PostgreSQL para Python.

## Componentes del Código

### 1. `cargar_codigos`

Esta función se encarga de cargar códigos de acceso de UniProt. Utiliza la configuración definida en `config.yaml` para establecer la conexión con la base de datos PostgreSQL. Una vez establecida la conexión, invoca la función `cargar_codigos_acceso` para realizar la carga de datos.

#### Proceso Detallado:

- Lee la configuración de `config.yaml`.
- Establece conexión con la base de datos PostgreSQL.
- Crea todas las tablas necesarias utilizando `Base.metadata.create_all`.
- Inicia una sesión de SQLAlchemy.
- Llama a `cargar_codigos_acceso` con los criterios de búsqueda y el límite especificados en la configuración.

### 2. `procesar_datos_uniprot`

Dependiendo de `cargar_codigos`, esta función se encarga de procesar los datos de UniProt. Sigue un proceso similar para conectarse a la base de datos y, una vez establecida la conexión, llama a `extraer_entradas` para procesar los datos.

#### Proceso Detallado:

- Lee la configuración de `config.yaml`.
- Establece conexión con la base de datos PostgreSQL.
- Crea todas las tablas necesarias si aún no existen.
- Inicia una sesión de SQLAlchemy.
- Llama a `extraer_entradas` para procesar los datos de UniProt.

## Configuración

El archivo `config.yaml` debe contener la configuración necesaria para la conexión a la base de datos y los parámetros de búsqueda en UniProt, incluyendo:

- `DB_USERNAME`: Nombre de usuario de la base de datos.
- `DB_PASSWORD`: Contraseña de la base de datos.
- `DB_HOST`: Host de la base de datos.
- `DB_PORT`: Puerto de la base de datos.
- `DB_NAME`: Nombre de la base de datos.
- `criterio_busqueda`: Criterio de búsqueda para UniProt.
- `limit`: Límite en el número de resultados a obtener.

---