# Checks de CI

Los workflows de GitHub Actions ejecutan comprobaciones en pushes a `develop` y `main`, y en Pull Requests cuyo destino sea cualquiera de esas ramas.

## Checks configurados

| Check | Qué valida |
| --- | --- |
| `CI / Backend CI Job` | Importación de FastAPI, pruebas backend y errores graves de Python con Flake8. |
| `CI / Frontend CI Job` | Instalación reproducible con `npm ci` y compilación Vite. |
| `CI / Check changed lines for whitespace errors` | Errores de whitespace en el diff de la rama. |
| `CI / Check links in README` | Existencia de destinos de archivos enlazados desde el README raíz. |
| `CI / lint-markdown` | Reglas Markdown en los archivos `.md` modificados. |
| `SonarCloud Code Analysis / Analyze Python and React` | Análisis estático del backend FastAPI y el frontend React, más el Quality Gate de SonarCloud. |

## SonarCloud

El repositorio debe estar importado y vinculado a GitHub en SonarCloud. En **Settings → Secrets and variables → Actions**, configura:

- **Secret** `SONAR_TOKEN`: token de análisis creado en SonarCloud.
- **Variable** `SONAR_ORGANIZATION`: clave de la organización SonarCloud.
- **Variable** `SONAR_PROJECT_KEY`: clave del proyecto SonarCloud.

No guardes el token en el repositorio ni lo escribas en el workflow. La acción de análisis usa el escáner oficial de SonarSource y espera el Quality Gate.

La documentación oficial explica cómo importar el repositorio y dónde obtener estos valores: [integración de SonarQube Cloud con GitHub](https://docs.sonarsource.com/sonarqube-cloud/getting-started/github) y [acción oficial de análisis](https://github.com/SonarSource/sonarqube-scan-action).

El análisis se omite para Pull Requests provenientes de forks, porque GitHub no entrega secretos del repositorio a esos workflows.

## Activación inicial

Los workflows nuevos deben integrarse en la rama destino antes de poder ejecutarse en Pull Requests hacia ella. Por eso, este PR de configuración puede no mostrar todavía los checks nuevos. Al integrarlo en `develop`, se activarán para futuros PR hacia `develop`; para PR hacia `main`, deben llegar también a `main` mediante el flujo normal de promoción.

Si se desea impedir la integración cuando falle una validación, configura estos nombres como checks obligatorios en las reglas de protección de ambas ramas. La ejecución de un workflow y su requisito de aprobación son configuraciones distintas.
