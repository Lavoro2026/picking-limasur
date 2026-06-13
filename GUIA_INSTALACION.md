# GUÍA DE INSTALACIÓN — Sistema Picking Lima Sur

## ¿Cómo funciona?

```
[Tu PC en el almacén]         [Internet - GitHub]         [Celulares de trabajadores]
  Archivo Excel del día   →   subir_picking.bat   →   picking_data.json   →   URL fija (app web)
```

Tú ejecutas el `.bat` cada vez que se actualiza el Excel, y en segundos los trabajadores ven los datos frescos en sus celulares (sin descargar nada, solo abriendo la URL).

---

## PASO 1 — Crear cuenta GitHub (5 minutos)

1. Ve a **https://github.com** desde cualquier PC con internet
2. Haz clic en **Sign up** y crea una cuenta gratuita
3. Elige como nombre de usuario algo como `almacenlimasur` o similar
4. Confirma el correo electrónico

---

## PASO 2 — Crear el repositorio (2 minutos)

1. Ya dentro de GitHub, haz clic en el botón verde **New** (o el ícono `+`)
2. En **Repository name** escribe: `picking-limasur`
3. Marca la opción **Public** (importante para que la app web lo lea)
4. Marca **Add a README file**
5. Haz clic en **Create repository**

---

## PASO 3 — Crear token de acceso (3 minutos)

El script necesita un "token" para subir archivos automáticamente.

1. En GitHub, haz clic en tu foto de perfil (arriba a la derecha) → **Settings**
2. En el menú izquierdo, baja hasta **Developer settings** (al final)
3. Haz clic en **Personal access tokens** → **Tokens (classic)**
4. Clic en **Generate new token** → **Generate new token (classic)**
5. En **Note** escribe: `Picking Lima Sur`
6. En **Expiration** elige **No expiration**
7. En **Select scopes** marca solo: ✅ **repo**
8. Clic en **Generate token**
9. **¡IMPORTANTE!** Copia el token que aparece (empieza con `ghp_...`)
   - Guárdalo en un bloc de notas porque solo se muestra una vez

---

## PASO 4 — Configurar el script Python

1. Abre el archivo `subir_picking.py` con el Bloc de notas
2. Cambia las líneas de configuración (están al inicio):

```python
GITHUB_USER  = "TU_USUARIO"       # ← Tu nombre de usuario de GitHub
GITHUB_REPO  = "picking-limasur"   # ← Déjalo igual
GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"  # ← Pega aquí tu token
CARPETA_EXCEL = r"Z:\Lima-Sur\AREA - ALMACEN LIMA SUR\PICKING\2026\06. JUNIO"
              # ↑ Esta ruta ya está configurada, actualízala según el mes
```

3. Guarda el archivo

---

## PASO 5 — Instalar Python (si no está instalado)

1. Ve a **https://www.python.org/downloads/windows/**
2. Descarga el instalador (Python 3.12 o similar)
3. Al instalar: **marca la casilla "Add Python to PATH"** (es clave)
4. Las librerías se instalan automáticamente la primera vez que ejecutes el `.bat`

---

## PASO 6 — Publicar la app web en GitHub Pages

Sube el archivo `index.html` al repositorio:

1. En tu repositorio GitHub, haz clic en **Add file** → **Upload files**
2. Arrastra el archivo `index.html`
3. Antes de subirlo, edita las líneas de configuración dentro del `index.html`:

```javascript
const GITHUB_USER = "TU_USUARIO";     // ← Tu usuario de GitHub
const GITHUB_REPO = "picking-limasur"; // ← Déjalo igual
```

4. Confirma el upload
5. Ve a **Settings** del repositorio → **Pages** (en el menú izquierdo)
6. En **Source** selecciona: `Deploy from a branch`
7. En **Branch** elige `main`, carpeta `/ (root)`
8. Haz clic en **Save**
9. Espera 2-3 minutos y tu app estará en:
   **`https://TU_USUARIO.github.io/picking-limasur/`**

Esta es la URL que compartes con los trabajadores — no cambia nunca.

---

## USO DIARIO

### Cada vez que el Excel se actualiza:

1. Haz doble clic en **SUBIR_PICKING.bat**
2. Espera unos segundos hasta que diga ✅ Datos subidos correctamente
3. Los trabajadores ya ven la info actualizada automáticamente
   (la app se refresca sola cada 3 minutos)

### Los trabajadores solo necesitan:

- Abrir Chrome/Safari en su celular
- Ir a la URL: `https://TU_USUARIO.github.io/picking-limasur/`
- Opcional: guardarla como acceso directo en la pantalla de inicio

---

## ACTUALIZAR LA CARPETA DEL MES

Cuando cambie el mes, edita esta línea en `subir_picking.py`:

```python
CARPETA_EXCEL = r"Z:\Lima-Sur\AREA - ALMACEN LIMA SUR\PICKING\2026\07. JULIO"
```

---

## SOLUCIÓN DE PROBLEMAS

| Problema | Solución |
|----------|----------|
| El `.bat` dice "No se encontró Python" | Instala Python y marca "Add to PATH" |
| Error "HTTP 401" | El token es incorrecto o venció, genera uno nuevo |
| Error "HTTP 404" | El repositorio no existe o el usuario está mal escrito |
| Los celulares ven datos viejos | Haz pull-to-refresh en el celular, o espera 3 min |
| No encuentra el archivo Excel | Verifica la ruta en `CARPETA_EXCEL` |
