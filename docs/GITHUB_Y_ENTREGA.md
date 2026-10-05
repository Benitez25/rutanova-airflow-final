# Publicación, PR y evidencia de entrega

## 1. Crear repositorio público

En GitHub: New repository → `rutanova-airflow` → Public. No añadas README/gitignore
remotos si vas a publicar esta carpeta. En terminal desde rutanova:

```bash
git init
git branch -M main
git add .gitignore .dockerignore .env.example README.md docs/GLOSARIO.md
git status
git commit -m "docs: define caso RutaNova y reglas de negocio"
git remote add origin https://github.com/TU_USUARIO/rutanova-airflow.git
git push -u origin main
git switch -c feat/pipeline-rutanova
```

Reemplaza TU_USUARIO por tu cuenta. Revisa/ejecuta cada bloque antes de incorporarlo:

```bash
git add Dockerfile docker-compose.yaml requirements.txt config scripts/configure.py scripts/generate_key.py scripts/bootstrap.py secrets/.gitkeep reports/.gitkeep
git commit -m "infra: configura Airflow y almacenamiento local"
git add api inbox src dags
git commit -m "feat: ingesta dos fuentes y carga snapshot atomico"
git add dbt sql
git commit -m "feat: modela y valida rentabilidad con dbt"
git add tests pytest.ini .github
git commit -m "test: incorpora reglas de negocio y CI"
git add docs scripts/generate_architecture.py VALIDACION.md
git commit -m "docs: incorpora arquitectura y guia de entrega"
git push -u origin feat/pipeline-rutanova
```

Los mensajes y separación ayudan a revisar, pero ejecutar esta secuencia de golpe
NO demuestra semanas de trabajo. El ZIP es una base generada: haz tus pruebas,
correcciones y revisiones con commits auténticos. No cambies fechas ni inventes
historial. Declara el apoyo usado según las reglas académicas de tu curso.

## 2. PR y CI

En GitHub crea Pull Request de feat/pipeline-rutanova → main. Espera ambos checks:
`business-tests` y `docker-dag-tests`. Si fallan, corrige en la misma rama y sube el
commit. El segundo construye Docker y dbt; puede tardar varios minutos.

CI prueba la infraestructura de la imagen y el parsing del proyecto; no demuestra
que Snowflake funciona. La evidencia de Snowflake sale del DAG verde y sus tests dbt.

## 3. Branch Protection

Settings → Branches → Add branch protection rule (o Rules → Rulesets, según la UI).
Selecciona main, exige PR antes del merge y **Require status checks to pass**.
Añade business-tests y docker-dag-tests después de que hayan corrido una vez.
Activa también prohibir force push. Guarda y captura evidencia de la regla.
Si hay otra persona en el equipo, solicita revisión del PR antes de mezclarlo.
No basta que el YAML exista: debe verse el check verde y la protección activa.

## 4. Revisar secretos

```bash
git status --short
git check-ignore .env secrets/snowflake_key.p8
git log --all -- .env
git ls-files secrets
```

.env y privada deben estar ignoradas; git log de .env debe estar vacío; secrets
sólo debe mostrar .gitkeep. Si se subió un secreto, revócalo/rota y limpia historial
antes de entrega. No basta borrarlo en el último commit.

## 5. Entregar

1. Ejecuta DAG, revisa Snowflake y guarda evidencia de dbt build aprobado.
2. Graba 5–8 min según DEMO.md y sube video con acceso de lectura al profesor.
3. Completa docs/arquitectura.json con integrantes, repo y video.
4. Regenera PDF; confirma que los enlaces abren desde otro navegador.
5. Entrega en un correo/formulario: URL GitHub pública, URL video y PDF adjunto.

Para regenerar el PDF después de completar docs/arquitectura.json:

```bash
python -m pip install reportlab
python scripts/generate_architecture.py
```

El resultado reemplaza docs/Arquitectura_RutaNova.pdf. Comprueba que conserve dos
páginas y que las URLs no estén pendientes antes de publicarlo.

No se ha creado repositorio, activado reglas, grabado video ni ejecutado Snowflake
por cuenta del alumno. Son acciones externas pendientes para completar la entrega.
