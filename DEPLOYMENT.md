# Despliegue y Debugging en Railway

## ✅ Bug Crítico Arreglado

**Problema que tenías**: Los mercados binarios sin `yes_token_id` pasaban el filtro de liquidez pero fallaban después, causando que pareciera "todos los mercados filtrados" cuando en realidad les faltaban tokens.

**Solución aplicada**: Ahora el código valida que los mercados tengan `yes_token_id` ANTES de verificar liquidez. Mercados sin tokens se saltan inmediatamente con un log claro:
```
[FILTER] Skipping binary market 'ABC...' - no yes_token_id (untradeable)
```

Este fix está en `opinion_trade_api.py` líneas 298-302.

---

## 🔍 Cómo Debuggear en Railway

### Opción 1: Ver Logs Directamente (Recomendado)

**Desde Replit usando Railway CLI:**

1. **Configurar Railway CLI** (una sola vez):
   ```bash
   ./scripts/setup_railway_cli.sh
   ```
   - Ve a https://railway.app/account/tokens
   - Crea un token de API
   - Agrégalo a Replit Secrets como `RAILWAY_TOKEN`
   - Re-ejecuta el script

2. **Ver logs en tiempo real**:
   ```bash
   ./scripts/tail_backend_logs.sh
   ```
   Esto muestra los logs de Railway directamente en Replit.

3. **Ejecutar comandos remotos**:
   ```bash
   ./scripts/run_remote_command.sh "curl localhost:8000/health"
   ```

**Desde Railway Web:**
- Ve a https://railway.app
- Abre tu proyecto TradingAgents
- Click en "View Logs"
- Busca por:
  - `[FILTER]` - Mercados filtrados
  - `[BET]` - Apuestas ejecutadas
  - `[SKIP]` - Decisiones rechazadas
  - `[ERROR]` - Errores

### Opción 2: Validar Localmente (Limitado)

Si tienes las credenciales configuradas en Replit:

```bash
# Verificar conexión al SDK
python scripts/health_check_opinion_trade.py

# Validación completa (requiere npm build)
scripts/simple_validate.sh
```

⚠️ **Nota**: Estos scripts requieren las mismas API keys que Railway, así que solo funcionan si configuras las secrets en Replit.

---

## 🚀 Workflow de Despliegue

### Antes de Deployar

1. **Revisar cambios**:
   ```bash
   git status
   git diff
   ```

2. **Opcional - Validar SDK** (si tienes secrets configuradas):
   ```bash
   python scripts/health_check_opinion_trade.py
   ```

3. **Commitear y pushear**:
   ```bash
   git add .
   git commit -m "Fix: liquidity filter validates tokens before checking orderbook"
   git push origin main
   ```

4. **Railway auto-deploya** desde GitHub.

### Después del Deploy

1. **Monitorear el deployment**:
   - Opción A: Railway Web → View Logs
   - Opción B: `./scripts/tail_backend_logs.sh`

2. **Verificar que funcione**:
   - Busca `[INFO] Opinion.trade API: Retrieved X active markets`
   - Busca `[FILTER] Skipping binary market` para confirmar el fix
   - Espera a ver `[BET]` o `[SKIP]` (decisiones de las IAs)

3. **Si hay problemas**:
   - Revisa los logs completos en Railway
   - Busca `[ERROR]` o `errno`
   - Verifica que esté en **Railway EU West** (no US)

---

## 🐛 Debugging de Problemas Comunes

### "All markets filtered out"

**Diagnóstico**:
```bash
# En Railway logs, busca:
[FILTER] Skipping binary market - no yes_token_id (untradeable)
[LIQUIDITY FILTER] Skipping binary market - no orderbook liquidity
```

**Causas**:
1. Mercados sin `yes_token_id` → Normal, ahora se filtran correctamente
2. Mercados sin liquidez → Normal, se filtran para ahorrar llamadas a IA
3. Todos son Sports → Normal, se filtran por categoría

**Solución**: Si TODOS los mercados se filtran, es un problema de Opinion.trade (no hay mercados tradeables en este momento).

### "Las IAs no hacen apuestas"

**Diagnóstico**:
```bash
# Busca en logs:
[BET]   # Si no aparece, busca:
[SKIP]  # Para ver por qué rechazaron
Expected Value  # Para ver los cálculos
```

**Causas**:
1. Todas las apuestas tienen EV negativo → Las IAs son conservadoras
2. Risk Guard bloqueó → Balance muy bajo
3. Error en APIs de IA → Revisa `[ERROR]`

**Solución**: Revisa los logs de `[SKIP]` para entender por qué rechazaron los mercados.

### "SDK errors (errno != 0)"

**Errores comunes**:
- `errno=10602`: Price con más de 3 decimales (ya arreglado)
- `errno=10403`: Geo-blocking → Verifica que Railway esté en **EU West**
- `errno=10001`: API key inválida → Verifica secrets

---

## 📚 Archivos Importantes

- `opinion_trade_api.py`: Bug fix del liquidity filter (líneas 298-302)
- `scripts/setup_railway_cli.sh`: Setup inicial de Railway CLI
- `scripts/tail_backend_logs.sh`: Ver logs en tiempo real
- `docs/railway-debugging.md`: Guía completa de debugging
- `replit.md`: Historial de cambios y arquitectura

---

## ✨ Próximos Pasos

1. **Pushea el código** a GitHub
2. **Railway auto-deploya**
3. **Monitorea los logs** para ver si el fix resuelve el problema
4. **Espera un ciclo completo** (cuando triggerees manualmente o por cron)
5. **Revisa los resultados** en el Admin Panel

Si ves logs como:
```
[FILTER] Skipping binary market 'XYZ' - no yes_token_id (untradeable)
[INFO] Opinion.trade API: Retrieved 71 active markets (skipped 45 markets - missing tokens or Sports category)
```

Entonces el fix está funcionando correctamente. Los mercados con tokens válidos pasarán al análisis de IA.
