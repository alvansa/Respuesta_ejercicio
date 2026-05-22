# Parte 1 — Google Cloud Platform

**Instrucciones:** Responde cada pregunta de forma concisa. No hay respuestas únicas correctas — nos interesa tu razonamiento y cómo tomas decisiones de diseño. Puedes usar listas, diagramas en texto o cualquier formato que te ayude a explicarte.

---

## Pregunta 1

El área de datos del CMS tiene hoy varios pipelines que corren localmente en un computador y generan archivos Excel como output. El equipo va a crecer y necesita que estos pipelines sean accesibles y ejecutables sin depender de una máquina local.

¿Cómo diseñarías la migración a GCP? Describe tu propuesta, los servicios que usarías y el orden en que lo harías.

**Respuesta:**

Se utilizaran 4 servicios principales Artifact Registry, Cloud Storage, Cloud Run y Cloud Scheduler. De manera extra se deberia utilizar BigQuery.


Para realizar la migracion seguiria los siguientes pasos
1) Empaquetar los scripts/pipelines actuales en docker para asegurar que funciones en local y en el servidor
2) Crear buckets de cloud storage que remplazaran las carpetas locales
3) Configurar un Cloud Run y subir los archivos docker a Artifact Registry (configurar variables ENV).
4) Automatizar y orquestar con Cloud Scheduler, usando Cloud Tasks para reintentos.
5) Documentar y eliminar pipelines locales. 

Tareas extras que se podrian realizar:
1) Migrar a BigQuery creando bases de datos en vez de generar excel, y cuando se necesiten excel generarlos bajo demanda.
2) Integrar Cloud Loggin y Cloud Monitoring para llevar un registro de logs y alertas.
Con este enfoque se minimizan los riesgos y se evita manejar servidores. Idealmente se realizaria una migracion gradual a BigQuery.
---

## Pregunta 2

El área de datos del CMS tiene tres bases de datos que deben estar disponibles en GCP. Los usuarios que acceden son:
  - Analistas de otras áreas del CMS: consultan los datos frecuentemente con filtros, sin necesidad de descargar archivos completos
  - Ingeniero de datos del CMS: lee y escribe en todas las bases, incluyendo cargar nuevas versiones
  - Organización externo: descarga versiones completas periódicamente, pero no tiene acceso a todas las bases

¿Cómo organizarías el almacenamiento y los permisos en GCP para este escenario?

**Respuesta:**

Primero que todo se deberia realizar la migracion a BigQuery como gran repositorio central donde cada base de datos se convierte en un dataset. Tambien configurar un pipeline para poder exportar los datos desde BigQuery a CVS/Excel dentro de un bucket de Cloud Storage especialmente para el perfil de externo. 

Luego se crearian 3 perfiles, uno para cada area:
- Analista: El analista debe poder acceder a ver los datos y filtrarlos pero no las metadatos ni subrutinas, por lo que se le entregarian permisos de bigQuery.dataViewer sobre los datasets y bigQuery.jobUser para ejecutar queries  .

- Ingeniero de datos: El ingeniero de datos debe tener acceso completo al CRUD, cargar versiones y esquemas por lo que tendra bigquery.dataEditor iam.serviceAccountUser para ejecutar cargas en especial desde cuentas de servicio,  storage.objectAdmin para manejar los backups de los buckets, bigQuery.jobUser para ejecutar queries y por ulitmo loggin.viewer para ver los logs.

- Externo: El externo debe ser capaz de descargar versiones completas pero como no puede ver datos restringidos lo mejor seria que tenga permisos de bigQuery.dataviewer con los datasets que necesita, y lo mejor seria entregar un Json con credenciales seguras y temporales.

Aparte se debe configurar Cloud Audit Logs para tener un registro de todos los accesos

---

*Centro de Movilidad Sostenible — cmsostenible.org*