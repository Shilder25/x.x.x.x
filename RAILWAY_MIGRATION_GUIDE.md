# 🚂 Railway Migration Guide - TradingAgents Framework

Esta guía te llevará paso a paso para migrar tu framework de AI trading desde Replit a Railway, desbloqueando el acceso a Opinion.trade desde servidores europeos o asiáticos.

## ⏱️ Tiempo estimado: 30-45 minutos

---

## 📋 Prerequisitos

Antes de comenzar, necesitas:

✅ **Cuenta en Railway** (gratuita)
- Regístrate en: https://railway.app
- Conecta tu cuenta de GitHub (recomendado) o usa email

✅ **Código en GitHub** (recomendado)
- Sube este proyecto a un repositorio privado de GitHub
- O prepara el código para upload manual desde tu computadora

✅ **Todas tus API keys listas** (12 variables de entorno)
- Las mismas que usas actualmente en Replit
- Ver sección "Variables de Entorno" más abajo

---

## 🚀 Paso 1: Crear Proyecto en Railway

### 1.1 Ingresar a Railway
1. Ve a https://railway.app
2. Click en **"Start a New Project"**
3. Selecciona **"Deploy from GitHub repo"** (si conectaste GitHub)
   - O selecciona **"Empty Project"** si vas a subir código manualmente

### 1.2 Conectar Repositorio (método GitHub)
1. Autoriza a Railway acceso a GitHub
2. Selecciona tu repositorio del framework
3. Railway detectará automáticamente:
   - 🐍 Python (pyproject.toml)
   - 🟢 Node.js (frontend/package.json)

### 1.3 Upload Manual (alternativa)
Si no usas GitHub:
1. Selecciona **"Empty Project"**
2. Ve a **Settings → Connect → GitHub** (o conecta CLI)
3. Usa Railway CLI: `railway link` y luego `railway up`

---

## ⚙️ Paso 2: Configurar Multi-Servicio

Railway necesita saber que tienes 2 servicios: Backend (Flask) y Frontend (Next.js).

### 2.1 Crear Servicio Backend (API)

1. En tu proyecto Railway, click **"+ New Service"**
2. Selecciona **"GitHub Repo"** (o tu método de deploy)
3. Configura:
   - **Service Name**: `api`
   - **Root Directory**: `/` (raíz del proyecto)
   - **Build Command**: `pip install --upgrade pip && pip install -e .`
   - **Start Command**: `python api.py`

4. En **Settings → Networking**:
   - **Port**: `8000`
   - Habilita **"Public Networking"**
   - Toma nota de la URL pública (ej: `api-production.up.railway.app`)

### 2.2 Crear Servicio Frontend (Next.js)

1. Click **"+ New Service"** nuevamente
2. Selecciona el mismo repositorio
3. Configura:
   - **Service Name**: `frontend`
   - **Root Directory**: `/frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run start`

4. En **Settings → Networking**:
   - **Port**: `5000`
   - Habilita **"Public Networking"**
   - Esta será tu URL principal para acceder al sitio

---

## 🌍 Paso 3: Seleccionar Región (CRÍTICO)

**Este es el paso más importante** para resolver el bloqueo de Opinion.trade.

### 3.1 Cambiar Región del Backend (API)

1. Ve al servicio `api`
2. Click en **Settings → General**
3. Busca **"Deploy Region"**
4. **Selecciona una región NO-US**:

**Recomendado (en orden de preferencia):**
- 🇪🇺 **`eu-west-1`** (Frankfurt, Germany) - MEJOR OPCIÓN
- 🇪🇺 **`eu-central-1`** (Paris, France)
- 🇸🇬 **`ap-southeast-1`** (Singapore)
- 🇦🇺 **`ap-southeast-2`** (Sydney, Australia)

5. Click **"Save"** - Railway redesplegará automáticamente

### 3.2 Región del Frontend

El frontend puede quedarse en US si quieres (más rápido para usuarios US), ya que:
- Solo el backend hace llamadas a Opinion.trade
- El frontend solo consume tu API Flask

**Opcional**: Cambia frontend a la misma región que el backend para minimizar latencia.

---

## 🔐 Paso 4: Configurar Variables de Entorno

Necesitas configurar las mismas 12+ variables que tienes en Replit.

### 4.1 Variables del Backend (servicio `api`)

1. Ve al servicio `api`
2. Click en **Variables** (tab superior)
3. Click **"+ New Variable"**
4. Agrega cada una de estas:

#### LLM APIs (5 variables)
```
AI_INTEGRATIONS_OPENAI_API_KEY = sk-...
AI_INTEGRATIONS_OPENAI_BASE_URL = https://api.openai.com/v1
DEEPSEEK_API_KEY = sk-...
QWEN_API_KEY = sk-...
XAI_API_KEY = xai-...
```

#### Financial Data APIs (2 variables)
```
ALPHA_VANTAGE_API_KEY = ...
OPINION_TRADE_API_KEY = ...
```

#### Reddit API (2 variables)
```
REDDIT_CLIENT_ID = ...
REDDIT_CLIENT_SECRET = ...
```

#### Opinion.trade Trading (1 variable CRÍTICA)
```
OPINION_WALLET_PRIVATE_KEY = 0x...
```
⚠️ **IMPORTANTE**: Esta es tu clave privada de BNB Chain. Guárdala segura.

#### Sistema (3 variables)
```
ADMIN_PASSWORD = tu_password_admin
BANKROLL_MODE = TEST
SYSTEM_ENABLED = true
```

#### Variables Adicionales Railway (2 variables)
```
PORT = 8000
PYTHONUNBUFFERED = 1
```

5. Click **"Add"** para cada variable

### 4.2 Variables del Frontend (servicio `frontend`)

1. Ve al servicio `frontend`
2. Click en **Variables**
3. Agrega:

```
NEXT_PUBLIC_API_URL = https://api-production.up.railway.app
PORT = 5000
```

⚠️ **Reemplaza** `https://api-production.up.railway.app` con la URL real de tu servicio `api` (del paso 2.1.4)

---

## 🔄 Paso 5: Deploy y Verificación

### 5.1 Iniciar Deploy

1. Railway desplegará automáticamente después de configurar las variables
2. Monitorea los logs en **Deployments → [último deployment] → Logs**
3. Espera a ver:
   - ✅ Backend: `"Running on http://0.0.0.0:8000"`
   - ✅ Frontend: `"Ready on http://0.0.0.0:5000"`

### 5.2 Verificar Conectividad

#### Test 1: Health Check del Backend
```bash
curl https://TU-API-URL.railway.app/health
```
Debería responder: `{"status": "healthy", ...}`

#### Test 2: Opinion.trade Markets (CRÍTICO)
```bash
curl https://TU-API-URL.railway.app/api/markets
```
**Si funciona**: Verás lista de mercados JSON (¡desbloqueado! 🎉)
**Si falla**: Revisa que seleccionaste región EU/Asia en Paso 3.1

#### Test 3: Frontend
1. Abre `https://TU-FRONTEND-URL.railway.app` en navegador
2. Deberías ver la interfaz Alpha Arena
3. Verifica que carga datos del backend

---

## 📊 Paso 6: Configuración de Base de Datos

Railway detecta `trading_agents.db` (SQLite), pero SQLite en Railway es efímero.

### Opción A: Continuar con SQLite (Simple)
- Funcionará, pero datos se pierden en cada redeploy
- OK para testing inicial

### Opción B: Migrar a PostgreSQL (Recomendado para producción)
1. En Railway, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway creará automáticamente:
   - Base de datos PostgreSQL
   - Variable `DATABASE_URL` en tu backend
3. Modificar `database.py` para usar PostgreSQL en lugar de SQLite
   - Cambiar `sqlite3` por `psycopg2` o SQLAlchemy
   - Usar `DATABASE_URL` de las variables de entorno

**Nota**: Para MVP, SQLite está bien. Migra a PostgreSQL cuando estés listo para producción.

---

## 💰 Paso 7: Monitoreo de Costos

Railway funciona con créditos pay-as-you-go.

### Plan Gratuito (Hobby)
- **$5 USD de crédito mensual** (gratis)
- Suficiente para testing/desarrollo
- ~100 horas de ejecución

### Uso Estimado (tu proyecto)
- **Backend Flask**: ~$0.002/hora = ~$1.50/mes (24/7)
- **Frontend Next.js**: ~$0.003/hora = ~$2.20/mes (24/7)
- **Total**: ~$3.70/mes dentro del plan gratuito ✅

### Cuando Necesites Más
- **Developer Plan**: $5/mes (incluye $5 de uso + extras)
- **Pro Plan**: $20/mes (para producción seria)

---

## ✅ Checklist Post-Deployment

Verifica cada uno antes de declarar éxito:

### Conectividad
- [ ] Backend responde en `/health`
- [ ] Frontend carga correctamente
- [ ] Frontend puede llamar al backend

### Opinion.trade (CRÍTICO)
- [ ] `/api/markets` retorna mercados reales (no error 10403)
- [ ] Región del backend es EU/Asia (no US)
- [ ] `OPINION_WALLET_PRIVATE_KEY` configurada correctamente

### LLMs
- [ ] Endpoint `/api/firms` retorna lista de 5 AI firms
- [ ] Cada LLM tiene API key configurada

### Sistema de Trading
- [ ] `BANKROLL_MODE=TEST` configurado
- [ ] Daily limits funcionan ($5/día)
- [ ] Base de datos se inicializa correctamente

### Seguridad
- [ ] Variables de entorno no aparecen en logs públicos
- [ ] Private key de wallet está en variables (no en código)
- [ ] `ADMIN_PASSWORD` es fuerte y única

---

## 🛠️ Troubleshooting

### Error: "Invalid area" (errno 10403)
**Causa**: Backend aún en región US
**Solución**: 
1. Ve a Settings → General → Deploy Region
2. Cambia a `eu-west-1` o `ap-southeast-1`
3. Espera redeploy automático

### Error: "Cannot connect to backend"
**Causa**: URL del backend incorrecta en frontend
**Solución**:
1. Verifica `NEXT_PUBLIC_API_URL` en variables del frontend
2. Debe incluir `https://` y apuntar a la URL pública del servicio `api`

### Error: "Module not found"
**Causa**: Dependencias no instaladas
**Solución**:
1. Verifica que `pyproject.toml` y `package.json` están en el repo
2. Revisa logs de build para ver qué falló
3. Puede necesitar agregar `build command` custom

### Deployment falla constantemente
**Solución**:
1. Revisa **Deployments → Logs** para error específico
2. Verifica que todas las variables de entorno estén configuradas
3. Prueba deploy local con Railway CLI: `railway run python api.py`

### Base de datos vacía después de redeploy
**Causa**: SQLite es efímero en Railway
**Solución**:
1. Migra a PostgreSQL (ver Paso 6)
2. O implementa seed script que recree datos en startup

---

## 📞 Soporte

### Railway
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Opinion.trade
- Docs: https://docs.opinion.trade
- Support: support@opinion.trade

---

## 🎯 Siguientes Pasos Post-Migración

Una vez funcionando en Railway:

1. **Validar Trading Real**
   - Hacer primera apuesta manual en `/admin`
   - Verificar que la orden aparece en Opinion.trade
   - Confirmar que balance se actualiza correctamente

2. **Activar Sistema Autónomo**
   - Configurar `SYSTEM_ENABLED=true`
   - Monitorear logs de autonomous_engine
   - Verificar daily_watchdog.py ejecuta correctamente

3. **Optimizar Costos**
   - Implementar auto-scale en Railway
   - Pausar servicios cuando no se usan
   - Considerar cron jobs para procesos batch

4. **Seguridad Adicional**
   - Habilitar autenticación en API endpoints
   - Configurar rate limiting
   - Implementar alertas de gastos inusuales

---

## 🎉 ¡Listo!

Si completaste todos los pasos, tu framework de AI trading ahora está:

✅ Desplegado en Railway (región EU/Asia)
✅ Con acceso completo a Opinion.trade
✅ Listo para trading real con los 5 AI agents
✅ Protegido con risk management de 4 niveles
✅ Monitoreado y escalable

**¡Hora de dejar que los AIs compitan! 🤖💰**
