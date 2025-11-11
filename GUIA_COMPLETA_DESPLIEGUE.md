# 📖 Guía Completa: Subir Código a GitHub y Desplegar en Railway

Esta guía te ayudará paso a paso a subir tu código a GitHub y desplegarlo en Railway para que funcione correctamente con Opinion.trade.

---

## 🎯 ¿Por qué Railway y no Vercel?

**Respuesta corta:** Opinion.trade bloquea servidores de EE.UU., y Replit solo tiene servidores ahí.

**Detalles:**
- Opinion.trade solo funciona desde servidores en Europa o Asia
- Replit solo ofrece servidores en EE.UU. o India
- Railway te permite elegir Frankfurt (Europa) o Singapur (Asia)
- Costo: ~$3.70/mes en Railway

---

## 📝 Parte 1: Subir el Código a GitHub

### Paso 1: Preparar Git en Replit

Abre la consola (Shell) en Replit y ejecuta estos comandos uno por uno:

```bash
# Configurar tu nombre (reemplaza con tu nombre)
git config --global user.name "Tu Nombre"

# Configurar tu email (el mismo de GitHub)
git config --global user.email "tu-email@ejemplo.com"
```

### Paso 2: Crear un Token de Acceso Personal en GitHub

1. Ve a GitHub: https://github.com/settings/tokens
2. Haz clic en **"Generate new token"** → **"Generate new token (classic)"**
3. En "Note" escribe: `Replit Deploy`
4. Marca la casilla **"repo"** (incluye todos los permisos de repo)
5. Haz clic en **"Generate token"** al final de la página
6. **IMPORTANTE:** Copia el token que aparece (algo como `ghp_xxxxxxxxxxxx`)
   - ⚠️ **Guárdalo en un lugar seguro, no lo podrás ver de nuevo**

### Paso 3: Conectar con tu Repositorio de GitHub

En la consola de Replit, ejecuta:

```bash
# Agregar el repositorio remoto (reemplaza con tu usuario)
git remote add origin https://github.com/Shilder25/x.x.x.x.git

# O si ya existe, actualízalo:
git remote set-url origin https://github.com/Shilder25/x.x.x.x.git
```

### Paso 4: Preparar los Archivos

```bash
# Ver qué archivos se van a subir
git status

# Agregar todos los archivos
git add .

# Crear un commit con un mensaje
git commit -m "Initial commit - TradingAgents framework"
```

### Paso 5: Subir a GitHub

```bash
# Subir el código (te pedirá usuario y contraseña)
git push -u origin main
```

**Cuando te pida credenciales:**
- **Username:** Tu usuario de GitHub (ejemplo: `Shilder25`)
- **Password:** El token que copiaste en el Paso 2 (NO tu contraseña de GitHub)

---

## 🚀 Parte 2: Desplegar en Railway

### Paso 1: Crear Cuenta en Railway

1. Ve a https://railway.app
2. Haz clic en **"Start a New Project"** o **"Login"**
3. Regístrate con tu cuenta de GitHub (es más fácil)

### Paso 2: Crear Nuevo Proyecto

1. En el dashboard de Railway, haz clic en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Busca y selecciona tu repositorio: `Shilder25/x.x.x.x`
4. Railway comenzará a detectar tu proyecto automáticamente

### Paso 3: Configurar el Backend (Servicio de API)

1. Railway creará automáticamente un servicio
2. Haz clic en el servicio creado
3. Ve a la pestaña **"Settings"**
4. En **"Service Name"** ponle: `backend`
5. En **"Start Command"** escribe:
   ```bash
   bash start-backend.sh
   ```
6. En **"Region"** selecciona:
   - **EU West (Frankfurt)** o
   - **Asia Southeast (Singapore)**
   - ⚠️ **IMPORTANTE: NO uses US East o US West**

### Paso 4: Agregar Variables de Entorno al Backend

1. En tu servicio backend, ve a la pestaña **"Variables"**
2. Haz clic en **"New Variable"** y agrega las siguientes (una por una):

```
AI_INTEGRATIONS_OPENAI_API_KEY=tu_api_key_aqui
AI_INTEGRATIONS_OPENAI_BASE_URL=https://api.openai.com/v1
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
REDDIT_CLIENT_ID=tu_client_id_aqui
REDDIT_CLIENT_SECRET=tu_client_secret_aqui
OPINION_TRADE_API_KEY=tu_api_key_aqui
DEEPSEEK_API_KEY=tu_api_key_aqui
QWEN_API_KEY=tu_api_key_aqui
XAI_API_KEY=tu_api_key_aqui
ADMIN_PASSWORD=tu_password_seguro
BANKROLL_MODE=TEST
OPINION_WALLET_PRIVATE_KEY=tu_private_key_aqui
PORT=8000
```

**⚠️ IMPORTANTE:** Copia los valores reales de tus secretos en Replit:
- En Replit, ve a "Tools" → "Secrets"
- Copia cada valor y pégalo en Railway

### Paso 5: Obtener la URL del Backend

1. Una vez desplegado, ve a la pestaña **"Settings"**
2. En **"Networking"**, haz clic en **"Generate Domain"**
3. Railway te dará una URL como: `backend-production-xxxx.up.railway.app`
4. **Copia esta URL, la necesitarás para el frontend**

### Paso 6: Crear el Servicio del Frontend

1. En tu proyecto de Railway, haz clic en **"New Service"**
2. Selecciona **"GitHub Repo"** → Elige el mismo repositorio
3. Nómbralo: `frontend`
4. En **"Settings"**:
   - **Root Directory:** `frontend`
   - **Start Command:** `npm run dev`
   - **Region:** Mismo que el backend (Frankfurt o Singapore)

### Paso 7: Configurar Variables de Entorno del Frontend

1. En el servicio `frontend`, ve a **"Variables"**
2. Agrega esta variable:

```
NEXT_PUBLIC_API_URL=https://tu-backend-url-aqui.up.railway.app
```

**Reemplaza** `tu-backend-url-aqui.up.railway.app` con la URL que copiaste en el Paso 5.

### Paso 8: Generar Dominio para el Frontend

1. En el servicio `frontend`, ve a **"Settings"**
2. En **"Networking"**, haz clic en **"Generate Domain"**
3. Railway te dará una URL como: `frontend-production-xxxx.up.railway.app`
4. **Esta es la URL de tu aplicación funcionando** 🎉

---

## ✅ Verificar que Todo Funciona

1. **Abre la URL del frontend** en tu navegador
2. **Verifica que los precios se cargan** (BTC, ETH, SOL, etc.)
3. **Revisa la página LIVE** para ver las predicciones de las IA
4. **Comprueba el Leaderboard** para ver las estadísticas

### Si los precios no cargan:

1. Ve a Railway → Servicio `backend` → **"Deployments"**
2. Haz clic en el último deployment
3. Revisa los logs para ver si hay errores
4. Verifica que todas las variables de entorno estén configuradas correctamente

### Si hay errores de CORS:

1. Ve al archivo `api.py` en tu repositorio
2. Busca la línea con `CORS(app`
3. Asegúrate de que incluye tu dominio de Railway

---

## 🔄 Actualizar el Código en el Futuro

Cuando hagas cambios en Replit y quieras actualizar Railway:

```bash
# En la consola de Replit:
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

Railway detectará automáticamente los cambios y redesplegar tu aplicación.

---

## 💰 Costos Estimados

- **Railway:** ~$3.70/mes con 2 servicios (backend + frontend)
- **Gratis:** $5 de crédito inicial para probar
- **Uso de APIs:** Depende del uso de OpenAI, Alpha Vantage, etc.

---

## 🆘 Solución de Problemas Comunes

### Error: "Permission denied"
```bash
# Ejecuta esto antes de push:
git remote set-url origin https://TU_TOKEN@github.com/Shilder25/x.x.x.x.git
```

### Error: "Invalid area" en Opinion.trade
- Verifica que seleccionaste **Frankfurt** o **Singapore** como región
- NO uses regiones de EE.UU.

### Frontend no se conecta al backend
- Verifica que `NEXT_PUBLIC_API_URL` en el frontend tenga la URL correcta
- La URL debe empezar con `https://` y NO terminar en `/`

### Variables de entorno no funcionan
- Después de agregar variables, haz clic en **"Redeploy"** en Railway
- Espera a que termine el despliegue (puede tomar 2-3 minutos)

---

## 📞 Contacto

Si tienes problemas, revisa:
1. Los logs en Railway (pestaña "Deployments" de cada servicio)
2. La consola del navegador (F12 → Console)
3. Que todas las API keys estén configuradas correctamente

---

**¡Listo! Tu aplicación debería estar funcionando en Railway con acceso completo a Opinion.trade** 🚀
