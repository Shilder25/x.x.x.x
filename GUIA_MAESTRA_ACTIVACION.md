# 🚀 Guía Maestra: Activar el Sistema Autónomo de Trading con IA

Esta guía te llevará paso a paso desde cero hasta tener las 5 IA (ChatGPT, Gemini, Qwen, Deepseek, Grok) haciendo predicciones automáticas con dinero real en Opinion.trade.

---

## 📋 Resumen de lo que Lograrás

Al terminar esta guía, tendrás:
- ✅ Backend y Frontend desplegados en Railway (Europa)
- ✅ Sistema autónomo ejecutándose automáticamente cada día
- ✅ 5 IA compitiendo con $50 de presupuesto ($5/día máximo)
- ✅ Dashboard en vivo mostrando predicciones y rendimiento
- ✅ Protección contra geo-bloqueo de Opinion.trade

---

## 🎯 Pasos Principales (Orden de Ejecución)

### PASO 1: Configurar Variables en Railway ⏱️ 10 minutos
**Archivo:** `CONFIGURAR_RAILWAY_VARIABLES.md`

**Qué hacer:**
1. Abre Railway → Proyecto → Servicio "keen-essence" (backend)
2. Ve a la pestaña "Variables"
3. Copia TODAS las variables de Replit Secrets a Railway (15 variables total)

**Variables críticas:**
- API keys de las 5 IA (OpenAI, Gemini, Qwen, Deepseek, XAI)
- Opinion.trade credenciales (API key + Private Key)
- Variables de control: `BANKROLL_MODE=TEST`, `SYSTEM_ENABLED=true`
- Seguridad: `CRON_SECRET` (crea una contraseña única)

**Resultado esperado:** Railway redespliega automáticamente en 2-3 minutos ✅

---

### PASO 2: Verificar el Sistema Localmente ⏱️ 5 minutos
**Archivo:** `DESPUES_DE_RAILWAY.md`

**Qué hacer:**
1. En Replit Shell, ejecuta: `python test_autonomous_system.py`
2. Verifica que las 4 pruebas pasen:
   - ✅ Conexión a Opinion.trade
   - ✅ Obtención de eventos
   - ✅ Predicción de ChatGPT
   - ✅ Base de datos funcional

**Resultado esperado:** 
```
✅ TODAS LAS PRUEBAS PASARON
El sistema está listo para ejecutar predicciones autónomas.
```

---

### PASO 3: Configurar Ejecución Automática Diaria ⏱️ 15 minutos
**Archivo:** `CONFIGURAR_CRON_RAILWAY.md`

**Qué hacer (OPCIÓN 1 - RECOMENDADA):**
1. Railway → "+ New" → GitHub Repo → Elige `Shilder25/x.x.x.x`
2. Nombra el servicio: **"ai-predictions-cron"**
3. Settings → Cron Schedule → Activa y configura: `0 9 * * *` (9 AM UTC diario)
4. Settings → Start Command: `python run_daily_cycle.py`
5. Copia todas las variables de "keen-essence" a "ai-predictions-cron"
6. Despliega

**Resultado esperado:** Railway ejecutará las predicciones automáticamente cada día a las 9 AM

---

### PASO 4: Verificar el Frontend ⏱️ 2 minutos

**Qué hacer:**
1. Abre: https://gentle-ambition-production.up.railway.app/
2. Verifica que veas:
   - ✅ Precios de criptomonedas actualizándose (BTC, ETH, SOL, etc.)
   - ✅ Tabla "The Contestants" con las 5 IA
   - ✅ Gráfico de rendimiento

**Resultado esperado:** La interfaz carga sin errores

---

### PASO 5: Ejecutar Primera Predicción Manual (OPCIONAL) ⏱️ 3 minutos

**Qué hacer:**
1. En Replit Shell: `python run_daily_cycle.py`
2. Observa el output completo del ciclo
3. Refresca el frontend para ver las predicciones

**Resultado esperado:**
```
✅ Ciclo completado en X segundos
✓ Apuestas realizadas: X
✓ Categorías analizadas: X
```

---

## 📊 Sistema en Funcionamiento

### ¿Qué Hace el Sistema Automáticamente?

Cada día a las 9 AM UTC (o la hora que configuraste):

1. **Busca Eventos:** Se conecta a Opinion.trade y obtiene mercados activos
2. **Análisis Multi-Fuente:** Cada IA analiza eventos usando 5 fuentes de datos:
   - 📈 Indicadores técnicos (Alpha Vantage)
   - 📰 Noticias financieras  
   - 📊 Datos fundamentales (Yahoo Finance)
   - 😊 Sentimiento de redes sociales (Reddit)
   - 📉 Volatilidad histórica

3. **Decisión Autónoma:** Cada IA decide si apostar basándose en:
   - Confianza en la predicción (>60% para apostar)
   - Riesgo del evento
   - Presupuesto disponible
   - Límites diarios ($5/día máximo en modo TEST)

4. **Ejecución:** Las apuestas se ejecutan en Opinion.trade usando USDT en BNB Chain

5. **Actualización:** El frontend muestra las nuevas predicciones automáticamente

---

## 💰 Modo TEST vs PRODUCTION

### Modo TEST (Actual)
```
BANKROLL_MODE = TEST
```
- Presupuesto inicial: **$50** total para las 5 IA
- Límite diario: **$5** combinado
- Protección automática contra pérdidas grandes
- **RECOMENDADO** hasta que estés 100% seguro

### Modo PRODUCTION (Para después)
```
BANKROLL_MODE = PRODUCTION
```
- Presupuesto inicial: **$5,000** total
- Sin límite diario
- Mayor exposición al riesgo
- ⚠️ **NO cambies hasta verificar que todo funciona perfectamente**

---

## 🔍 Monitoreo y Verificación

### Ver Logs del Sistema Autónomo

**En Railway:**
1. Servicio "ai-predictions-cron" → Deployments → View Logs
2. Busca:
   ```
   🤖 INICIO DEL CICLO DIARIO DE PREDICCIONES
   ✓ Apuestas realizadas: X
   ✅ Ciclo completado
   ```

**En el Frontend:**
1. https://gentle-ambition-production.up.railway.app/
2. Pestaña "LIVE" → Gráfico muestra rendimiento en tiempo real
3. Pestaña "LEADERBOARD" → Tabla con estadísticas de cada IA

---

## 🆘 Solución de Problemas Comunes

### Problema 1: "No veo predicciones en el frontend"

**Causas posibles:**
- Las IA aún no han ejecutado el primer ciclo
- No hay eventos disponibles en Opinion.trade
- El sistema está configurado con `SYSTEM_ENABLED=false`

**Solución:**
1. Ejecuta manualmente: `python run_daily_cycle.py`
2. Verifica que `SYSTEM_ENABLED=true` en Railway
3. Revisa los logs del servicio cron

---

### Problema 2: "El servicio cron no se ejecuta"

**Causas posibles:**
- Expresión cron incorrecta
- Variables de entorno no copiadas
- Start command incorrecto

**Solución:**
1. Verifica la expresión cron en https://crontab.guru
2. Asegúrate de que `python run_daily_cycle.py` esté en Start Command
3. Confirma que TODAS las variables estén copiadas del backend

---

### Problema 3: "Opinion.trade devuelve errores"

**Causas posibles:**
- API key incorrecta
- Private key inválida
- Fondos insuficientes en la wallet

**Solución:**
1. Verifica las credenciales en Railway Variables
2. Confirma que la wallet `0x43C9bAd451ed65b5268cec681FCe42AdA00Fc675` tiene fondos
3. Revisa los logs para el error específico

---

### Problema 4: "Las IA no apuestan nada"

**Esto es NORMAL.** Las IA son cautelosas y solo apuestan cuando:
- ✅ Confianza >60%
- ✅ Riesgo aceptable
- ✅ Evento con suficiente liquidez
- ✅ No se ha alcanzado el límite diario

**No es un error**, es el sistema funcionando correctamente.

---

## 📈 Métricas de Éxito

Sabrás que el sistema funciona bien cuando veas:

### Después de 1 semana:
- ✅ Al menos 3-5 predicciones ejecutadas
- ✅ Todas las IA con alguna actividad
- ✅ Balance total aún en modo TEST ($50 - gastos)

### Después de 1 mes:
- ✅ Suficientes datos para comparar IA (win rate, ROI)
- ✅ El sistema se ejecuta sin errores consistentemente
- ✅ Listo para considerar modo PRODUCTION

---

## ⚙️ Configuración Avanzada (Opcional)

### Cambiar Horario de Ejecución

Edita la expresión cron en Railway → ai-predictions-cron → Settings → Cron Schedule:

```bash
0 15 * * *     # 3 PM UTC (9 AM EST)
0 0 * * *      # Medianoche UTC
0 6 * * 1-5    # 6 AM UTC solo días de semana
```

### Cambiar a Modo PRODUCTION

⚠️ **Solo cuando estés 100% seguro:**

1. Railway → keen-essence → Variables
2. Cambia: `BANKROLL_MODE = PRODUCTION`
3. Cambia: presupuesto inicial se vuelve $5,000
4. Deploy

---

## 📚 Archivos de Referencia

- **CONFIGURAR_RAILWAY_VARIABLES.md** → Paso a paso de variables
- **CONFIGURAR_CRON_RAILWAY.md** → Detalles del cron job
- **DESPUES_DE_RAILWAY.md** → Pruebas y verificación
- **INSTRUCCIONES_GITHUB.md** → Cómo subir cambios a GitHub
- **test_autonomous_system.py** → Script de prueba
- **run_daily_cycle.py** → Script que ejecuta el cron

---

## ✅ Checklist Final

Antes de dar por terminado, verifica:

- [ ] Todas las variables configuradas en Railway (backend)
- [ ] Servicio cron creado y desplegado
- [ ] Test manual pasó exitosamente (`python test_autonomous_system.py`)
- [ ] Frontend carga correctamente (precios visibles)
- [ ] Expresión cron configurada correctamente
- [ ] `SYSTEM_ENABLED=true` y `BANKROLL_MODE=TEST`
- [ ] Logs del backend muestran inicialización exitosa
- [ ] Primer ciclo manual ejecutado sin errores

---

## 🎉 ¡Felicidades!

Si llegaste hasta aquí y completaste todos los pasos, tu sistema autónomo de trading con IA está funcionando. Las 5 IA ahora competirán diariamente en Opinion.trade, analizando eventos y haciendo predicciones de forma autónoma.

**Próximos pasos:**
1. Monitorea el sistema durante 1-2 semanas
2. Revisa los logs y el frontend regularmente
3. Cuando estés listo, considera cambiar a modo PRODUCTION
4. Ajusta estrategias según el rendimiento de cada IA

**¿Necesitas ayuda?** Revisa la sección "Solución de Problemas" o consulta los archivos de documentación específicos.

---

**Sistema creado por:** TradingAgents Framework  
**Versión:** 1.0  
**Última actualización:** Nov 2025
