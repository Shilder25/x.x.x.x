# Railway Log Access Setup

## ❌ Problema Actual

Railway CLI no funciona con Project Tokens. Necesitamos usar Railway's GraphQL API directamente.

## ✅ Solución: Configurar Account Token

### Paso 1: Crear Account Token en Railway

1. **Ve a Railway Dashboard**:
   https://railway.app/account/tokens

2. **Click "Create Token"**

3. **IMPORTANTE**: 
   - **NO selecciones ningún proyecto** (déjalo en blanco)
   - Esto crea un "Account Token" que funciona con la API

4. **Nombra el token**: Por ejemplo "Replit Access"

5. **Click "Create"**

6. **Copia el token completo** (empieza con algo como `e36684c7-...`)

### Paso 2: Agregar a Replit Secrets

1. **En Replit, abre el panel de Secrets** (icono de candado 🔒 en la barra lateral)

2. **Click "+ New Secret"**

3. **Configura así**:
   ```
   Key:   RAILWAY_API_TOKEN
   Value: [pega el token que copiaste]
   ```
   ⚠️ **IMPORTANTE**: El nombre debe ser exactamente `RAILWAY_API_TOKEN` (no `RAILWAY_TOKEN`)

4. **Click "Add Secret"**

### Paso 3: Verificar

Una vez agregado el secret, ejecuta:

```bash
python3 scripts/fetch_railway_logs.py
```

Deberías ver información sobre tus deployments en Railway.

## 🔍 Para Ver Logs

```bash
# Ver últimos 100 logs
python3 scripts/fetch_railway_logs.py

# Ver más logs
python3 scripts/fetch_railway_logs.py -n 500

# Filtrar por patrón
python3 scripts/fetch_railway_logs.py -f "ORDERBOOK DEBUG"
```

## ⚠️ Troubleshooting

**Error: "RAILWAY_API_TOKEN not set"**
- Verifica que el secret esté agregado en Replit
- El nombre debe ser exactamente `RAILWAY_API_TOKEN`
- Reinicia el shell si acabas de agregar el secret

**Error: "401 Unauthorized"**
- El token puede estar expirado
- Crea un nuevo Account Token en Railway
- Asegúrate de que sea Account Token, NO Project Token

**Error: "No deployments found"**
- Verifica que SERVICE_ID y ENVIRONMENT_ID sean correctos
- Revisa que el servicio tenga deployments en Railway

## 📚 Referencias

- Railway API Docs: https://docs.railway.com/reference/public-api
- Railway Tokens: https://railway.app/account/tokens
