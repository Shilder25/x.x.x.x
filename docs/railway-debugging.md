# Railway Debugging Guide

## 🎯 Objetivo

Este documento explica cómo **validar y debuggear tu aplicación ANTES de deployar a Railway**, evitando costosos ciclos de deploy fallidos.

## 📋 Pre-requisitos

1. **Railway Token**: Obtén un token de API en [Railway Account Tokens](https://railway.app/account/tokens)
2. **Replit Secrets**: Agrega el token como `RAILWAY_TOKEN` en Replit Secrets
3. **Railway CLI**: El script de setup lo instalará automáticamente

## 🚀 Setup Inicial

### Paso 1: Configurar Railway CLI

```bash
./scripts/setup_railway_cli.sh
```

Esto instalará Railway CLI y verificará la autenticación.

### Paso 2: Enlazar al Proyecto Railway

```bash
railway link
```

Selecciona tu proyecto `TradingAgents` de la lista.

## 🔍 Comandos de Debugging

### Ver Logs en Tiempo Real

```bash
./scripts/tail_backend_logs.sh
```

Esto mostrará los logs de Railway en tiempo real, incluyendo:
- `[BET]` - Decisiones de apuesta de las IAs
- `[SKIP]` - Mercados rechazados
- `[CATEGORY]` - Clasificación de mercados
- `[ERROR]` - Errores críticos
- `[LIQUIDITY FILTER]` - Resultados del filtro de liquidez

**Buscar patrones específicos:**

```bash
railway logs | grep -E "\[BET\]|\[SKIP\]|\[ERROR\]"
```

### Ejecutar Comandos Remotos

```bash
./scripts/run_remote_command.sh "python --version"
./scripts/run_remote_command.sh "cat autonomous_cycle.log"
./scripts/run_remote_command.sh "curl localhost:8000/health"
```

### Verificar Status del Deploy

```bash
railway status
```

## ✅ Validación Pre-Deploy

**CRÍTICO: Ejecuta esto ANTES de cada deploy a Railway**

```bash
make validate
```

Este comando ejecuta:
1. ✓ Tests unitarios (pytest)
2. ✓ Tests de integración (liquidity filter, autonomous flow)
3. ✓ Health check del SDK de Opinion.trade
4. ✓ Lint del frontend (Next.js)
5. ✓ Build del frontend (verifica que compile)

Si `make validate` pasa ✅, es **SEGURO deployar a Railway**.

## 🧪 Testing Local

### Health Check del SDK

```bash
python scripts/health_check_opinion_trade.py
```

Verifica:
- Variables de entorno configuradas
- SDK inicializado correctamente
- Balance de wallet accesible
- Mercados fetcheables
- Orderbook accesible

### Tests de Integración

```bash
# Test específico del liquidity filter fix
pytest tests/integration/test_liquidity_filter.py -v

# Todos los tests de integración
make test-integration
```

### Tests Unitarios

```bash
make test-unit
```

## 🐛 Debugging de Problemas Comunes

### Problema: "No markets found after filters"

**Diagnóstico:**
```bash
railway logs | grep "LIQUIDITY FILTER"
railway logs | grep "Retrieved.*active markets"
```

**Causas comunes:**
1. Todos los mercados sin liquidez
2. Mercados sin `yes_token_id` (bug del filtro - ahora arreglado)
3. Todos los mercados son de Sports (filtrados por categoría)

**Solución:**
- Ver el log completo para identificar cuántos mercados se skipearon y por qué
- Verificar que el fix del liquidity filter esté deployado

### Problema: "IAs no hacen apuestas"

**Diagnóstico:**
```bash
railway logs | grep "\[BET\]"
railway logs | grep "\[SKIP\]"
railway logs | grep "Expected Value"
```

**Causas comunes:**
1. Todos los mercados tienen EV negativo (las IAs son conservadoras)
2. Risk Guard bloqueó las apuestas (balance muy bajo)
3. Error en las llamadas a las APIs de las IAs

**Solución:**
- Revisar los logs de `[SKIP]` para ver por qué rechazaron los mercados
- Verificar balance del wallet: `railway logs | grep "balance"`
- Verificar tier de riesgo: `railway logs | grep "TIER"`

### Problema: "SDK errors (errno != 0)"

**Diagnóstico:**
```bash
railway logs | grep "errno"
railway logs | grep "SDK Error"
```

**Errores comunes:**
- `errno=10602`: Price has more than 3 decimals (arreglado en código)
- `errno=10403`: Invalid area (geo-blocking - necesita Railway EU West)
- `errno=10001`: API key invalid

**Solución:**
- Verificar que Railway esté en **EU West** (no US)
- Ejecutar health check: `python scripts/health_check_opinion_trade.py`

## 🔄 Workflow Completo de Deploy

```bash
# 1. Hacer cambios en el código
vim autonomous_engine.py

# 2. VALIDAR LOCALMENTE (CRÍTICO)
make validate

# 3. Si pasa, commitear y pushear
git add .
git commit -m "Fix: liquidity filter validates tokens before checking liquidity"
git push origin main

# 4. Railway auto-deploya desde GitHub

# 5. Monitorear deployment
railway logs --follow

# 6. Verificar health después del deploy
./scripts/run_remote_command.sh "curl localhost:8000/health"
```

## 📊 Interpretando Logs de Railway

### Log de Ciclo Exitoso

```
[INFO] Opinion.trade API: Retrieved 71 active markets
[LIQUIDITY FILTER] Skipping binary market 'XYZ...' - no orderbook liquidity
[CATEGORY] Analyzing Crypto market: 'Bitcoin to $100k by Dec 2024?'
[BET] ChatGPT-Firm: YES @ $0.45 (prob=65%, EV=+0.12, amount=$5.00)
[EXECUTION] Order placed successfully: order_id=abc123
```

### Log de Problema

```
[INFO] Opinion.trade API: Retrieved 71 active markets
[FILTER] Skipping binary market 'ABC...' - no yes_token_id (untradeable)
[FILTER] Skipping binary market 'DEF...' - no yes_token_id (untradeable)
...
[INFO] No markets found after filters
```

Esto indica que el problema está en los datos de Opinion.trade (mercados sin tokens), no en tu código.

## 🆘 Troubleshooting

### Railway CLI no autentica

```bash
# Verificar que el token esté configurado
echo $RAILWAY_TOKEN

# Re-ejecutar setup
./scripts/setup_railway_cli.sh
```

### No puedo ver logs de Railway

```bash
# Verificar conexión
railway status

# Re-enlazar al proyecto
railway link
```

### `make validate` falla

```bash
# Ver exactamente qué paso falla
make validate

# Ejecutar pasos individuales
make test-unit
make health-check
make build
```

## 📚 Referencias

- [Railway CLI Docs](https://docs.railway.app/develop/cli)
- [Opinion.trade SDK Docs](https://github.com/opinion-trade/opinion-clob-sdk)
- [TradingAgents replit.md](../replit.md)
