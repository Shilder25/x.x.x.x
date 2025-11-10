# 🚂 Railway Migration - Ready to Deploy

## ✅ Estado: Listo para migración

Tu proyecto TradingAgents está **100% preparado** para migrar a Railway y resolver el bloqueo geográfico de Opinion.trade.

---

## 📦 Archivos de Configuración Creados

### 1. `railway.toml`
Configuración multi-servicio para Railway que define:
- **Servicio `api`**: Backend Flask en puerto 8000
- **Servicio `frontend`**: Frontend Next.js en puerto 5000
- Healthchecks automáticos para monitoreo
- Comandos de build y start optimizados

### 2. `RAILWAY_MIGRATION_GUIDE.md` (⭐ ARCHIVO PRINCIPAL)
Guía paso a paso completa con:
- 7 pasos detallados desde crear cuenta hasta verificación final
- Tiempo estimado: 30-45 minutos
- Screenshots conceptuales de cada paso
- Troubleshooting de errores comunes
- Checklist de 14 puntos para verificar éxito

**👉 EMPIEZA AQUÍ**: Este es tu archivo principal para la migración.

### 3. `RAILWAY_ENV_VARS.md`
Referencia rápida de variables de entorno:
- Lista completa de 17 variables requeridas
- Tabla organizada por categoría (LLMs, APIs, Sistema)
- Valores de ejemplo
- Instrucciones para obtener cada API key
- Plantilla copy/paste lista para usar

### 4. Código Actualizado

**Backend (`api.py`)**:
- ✅ Nuevo endpoint `/health` agregado
- ✅ Monitorea estado de DB y API keys
- ✅ Responde con JSON para Railway healthcheck

**Frontend (`frontend/lib/config.ts` + `frontend/app/page.tsx`)**:
- ✅ Configuración centralizada de API URL
- ✅ Usa `NEXT_PUBLIC_API_URL` de Railway
- ✅ Fallback a `localhost:8000` para desarrollo local
- ✅ Todas las 6 llamadas fetch actualizadas

---

## 🎯 Próximos Pasos (En Orden)

### Paso 1: Lee la Guía (5 min)
```bash
# Abre este archivo en tu editor favorito:
RAILWAY_MIGRATION_GUIDE.md
```

### Paso 2: Sube tu Código a GitHub (10 min)
Railway funciona mejor con GitHub. Si aún no has subido tu código:

1. Ve a https://github.com/new
2. Crea un repositorio privado (ej: `tradingagents-framework`)
3. Sube todo el código de este proyecto
4. Asegúrate de incluir todos los archivos (especialmente `railway.toml`)

**Archivos críticos para incluir**:
- `railway.toml`
- `pyproject.toml`
- `api.py`
- `frontend/` (toda la carpeta)
- Todos los `.py` del backend

**Archivos a excluir** (crea `.gitignore`):
```
trading_agents.db
*.pyc
__pycache__/
node_modules/
.next/
.env
```

### Paso 3: Crea Cuenta en Railway (2 min)
1. Ve a https://railway.app
2. Click "Start a New Project"
3. Conecta tu cuenta de GitHub
4. Autoriza acceso a tu repositorio

### Paso 4: Sigue la Guía Completa (20-30 min)
Abre `RAILWAY_MIGRATION_GUIDE.md` y sigue **cada paso** en orden:

1. ✅ Crear proyecto Railway
2. ✅ Configurar servicios (api + frontend)
3. ✅ **CRÍTICO**: Seleccionar región EU/Asia (no US)
4. ✅ Configurar 17 variables de entorno
5. ✅ Deploy y monitoreo
6. ✅ Verificación con `/health` y `/api/markets`
7. ✅ Checklist final

### Paso 5: Primer Test (5 min)
Una vez desplegado, verifica:

```bash
# 1. Backend health
curl https://TU-API-URL.railway.app/health

# 2. Opinion.trade desbloqueado (¡lo más importante!)
curl https://TU-API-URL.railway.app/api/markets

# 3. Frontend carga
# Abre en navegador: https://TU-FRONTEND-URL.railway.app
```

**✅ Éxito**: Si `/api/markets` retorna JSON con mercados (no error 10403)

---

## 🌍 Regiones Recomendadas

Para evitar el geo-block de Opinion.trade, despliega el backend en:

1. **`eu-west-1`** (Frankfurt, Germany) - **MEJOR OPCIÓN** ⭐
2. **`eu-central-1`** (Paris, France)
3. **`ap-southeast-1`** (Singapore)
4. **`ap-southeast-2`** (Sydney, Australia)

❌ **NO uses**: `us-west-1`, `us-east-1` o cualquier región US

---

## 💰 Costos Estimados

| Plan | Costo mensual | Tu uso estimado |
|------|---------------|-----------------|
| **Hobby (Gratis)** | $0 (incluye $5 créditos) | ~$3.70/mes ✅ |
| **Developer** | $5/mes + uso | Si necesitas más |
| **Pro** | $20/mes + uso | Para producción seria |

**Conclusión**: El plan gratuito es suficiente para tu MVP y testing inicial.

---

## ⚠️ Notas Importantes

### Base de Datos SQLite
**Problema**: SQLite en Railway es efímero (se borra en cada redeploy).

**Soluciones**:
1. **Corto plazo**: Acepta que datos se borran (OK para MVP)
2. **Largo plazo**: Migra a PostgreSQL (Railway lo ofrece gratis)

La guía incluye instrucciones para PostgreSQL cuando estés listo.

### Variables de Entorno Sensibles
**NUNCA** subas a GitHub:
- `OPINION_WALLET_PRIVATE_KEY`
- API keys de LLMs
- `ADMIN_PASSWORD`

Estas solo deben estar en Railway (Variables tab).

### Monitoreo Inicial
Durante las primeras 24-48 horas después del deploy:
- Revisa logs en Railway cada 2-3 horas
- Verifica que las apuestas autónomas funcionan
- Monitorea balance en Opinion.trade

---

## 📞 Soporte y Recursos

### Railway
- **Docs**: https://docs.railway.app
- **Discord**: https://discord.gg/railway (comunidad muy activa)
- **Status**: https://status.railway.app

### Opinion.trade
- **API Docs**: https://docs.opinion.trade
- **Support**: support@opinion.trade

### Este Proyecto
Si algo falla durante la migración:
1. Revisa sección "Troubleshooting" en `RAILWAY_MIGRATION_GUIDE.md`
2. Verifica logs en Railway Dashboard
3. Confirma que todas las 17 variables están configuradas

---

## 🎉 Checklist Final Pre-Migración

Antes de empezar, confirma que tienes:

- [ ] Código subido a GitHub (repositorio privado)
- [ ] Cuenta en Railway creada
- [ ] Todas las 12 API keys listas (ver `RAILWAY_ENV_VARS.md`)
- [ ] Wallet de BNB Chain con private key
- [ ] Fondos en la wallet (USDT en BNB Chain)
- [ ] 30-45 minutos de tiempo disponible
- [ ] `RAILWAY_MIGRATION_GUIDE.md` abierto y listo

---

## 🚀 ¡Listo para Despegar!

Tienes todo lo necesario para migrar exitosamente:

✅ Archivos de configuración listos
✅ Código actualizado para multi-servicio
✅ Guía completa paso a paso
✅ Variables de entorno documentadas
✅ Troubleshooting preparado

**Siguiente acción**: Abre `RAILWAY_MIGRATION_GUIDE.md` y comienza en el **Paso 1**.

Una vez completada la migración, tus 5 AI agents (ChatGPT, Gemini, Qwen, Deepseek, Grok) estarán compitiendo en Opinion.trade con acceso real desde Europa/Asia.

**¡Buena suerte! 🤖💰**
