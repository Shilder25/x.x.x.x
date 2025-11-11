# ⏰ Configurar Ejecución Automática Diaria en Railway

## ¿Qué es esto?

Vamos a hacer que las 5 IA analicen eventos y hagan predicciones **automáticamente cada día** sin que tengas que hacer nada. Railway ejecutará el sistema todos los días a la hora que elijas.

---

## 📋 Requisitos Previos

Antes de configurar el cron job, asegúrate de haber:
- ✅ Configurado TODAS las variables de entorno en Railway (ver `CONFIGURAR_RAILWAY_VARIABLES.md`)
- ✅ Verificado que el backend se desplegó correctamente
- ✅ Probado que el sistema funciona manualmente (ver `DESPUES_DE_RAILWAY.md`)

---

## 🚀 Cómo Configurar el Cron Job (2 opciones)

Railway ofrece dos formas de ejecutar tareas programadas. Te recomiendo la **Opción 1** (más simple):

---

## ✨ OPCIÓN 1: Crear un Servicio Cron Separado (RECOMENDADO)

### Paso 1: Crear un Nuevo Servicio en Railway

1. Ve a tu proyecto en Railway
2. Click en **"+ New"** (arriba a la derecha)
3. Selecciona **"GitHub Repo"**
4. Elige el mismo repositorio: `Shilder25/x.x.x.x`
5. Ponle nombre al servicio: **"ai-predictions-cron"**

### Paso 2: Configurar el Servicio como Cron Job

1. En el nuevo servicio **"ai-predictions-cron"**, ve a **Settings**
2. Busca la sección **"Cron Schedule"**
3. Activa el toggle para habilitar cron
4. Ingresa la expresión cron (ejemplos abajo)

**Expresiones cron comunes:**
```bash
# Todos los días a las 9 AM (hora UTC)
0 9 * * *

# Todos los días a la medianoche (00:00 UTC)
0 0 * * *

# Todos los días a las 3 PM (15:00 UTC)
0 15 * * *

# Solo días de semana a las 10 AM
0 10 * * 1-5
```

💡 **Tip:** USA https://crontab.guru para crear tu expresión personalizada

⚠️ **IMPORTANTE:** Railway usa hora UTC, no tu zona horaria local. Ajusta en consecuencia.

### Paso 3: Configurar el Comando de Inicio

1. En **Settings**, busca **"Start Command"**
2. Ingresa exactamente esto:

```bash
python run_daily_cycle.py
```

### Paso 4: Copiar Variables de Entorno

El servicio cron necesita las MISMAS variables que el backend:

1. Ve al servicio **"keen-essence"** (tu backend)
2. Pestaña **"Variables"** → Click en los 3 puntos (...) → **"Copy to Clipboard"**
3. Ve al servicio **"ai-predictions-cron"**
4. Pestaña **"Variables"** → Click **"RAW Editor"** → Pega todo
5. Click **"Save"**

### Paso 5: Desplegar

Railway desplegará automáticamente. Ahora el sistema:
- ✅ Se ejecutará automáticamente cada día a la hora configurada
- ✅ Solo consumirá recursos durante la ejecución (1-5 minutos)
- ✅ Se apagará solo después de completar

---

## 🔧 OPCIÓN 2: Endpoint HTTP + Servicio Externo

Si prefieres usar un servicio de cron externo (como cron-job.org):

⚠️ **IMPORTANTE:** Esta opción requiere configurar el `CRON_SECRET` para seguridad.

### Paso 1: Configurar la Variable CRON_SECRET

El endpoint está protegido con autenticación para evitar ejecuciones no autorizadas.

1. Ve a Railway → Servicio "keen-essence" → Variables
2. Agrega una nueva variable:
   ```
   CRON_SECRET = [Una contraseña segura que TÚ crees, ej: mi-password-secreto-12345]
   ```
3. **Guarda bien esta contraseña**, la necesitarás para configurar el cron externo

### Paso 2: Configurar Cron-Job.org

1. Ve a https://cron-job.org (gratis)
2. Crea una cuenta
3. Click **"Create cronjob"**
4. Configura:
   - **URL:** `https://keen-essence-production.up.railway.app/api/run-daily-cycle`
   - **Schedule:** Diario a la hora que quieras
   - **Method:** POST
   - **Request headers:** Agregar header personalizado:
     - Header name: `X-Cron-Secret`
     - Header value: [El mismo CRON_SECRET que configuraste en Railway]
5. Guarda

⚠️ **Problemas de esta opción:**
- El backend estará activo 24/7 consumiendo recursos ($$$)
- Requiere configuración adicional de seguridad
- **Recomendación:** Usa OPCIÓN 1 en su lugar

---

## 📊 ¿Cómo Verificar que Funciona?

### Opción 1 (Servicio Cron):

1. Ve al servicio **"ai-predictions-cron"** en Railway
2. Pestaña **"Deployments"**
3. Verás ejecuciones programadas con logs
4. Click en **"View Logs"** para ver:
   ```
   🤖 INICIO DEL CICLO DIARIO DE PREDICCIONES
   ✓ Apuestas realizadas: X
   ✓ Categorías analizadas: X
   ✅ Ciclo completado en X segundos
   ```

### Opción 2 (Endpoint HTTP):

1. Revisa los logs del backend en Railway
2. Busca mensajes de ejecución del ciclo diario

---

## 🧪 Probar Manualmente (Sin Esperar al Cron)

Para probar que el cron job funciona SIN esperar al horario programado:

### Si usas Opción 1:
```bash
# En Replit Shell:
python run_daily_cycle.py
```

### Si usas Opción 2:
```bash
# En Replit Shell o Postman (requiere CRON_SECRET):
curl -X POST \
  -H "X-Cron-Secret: TU_CRON_SECRET_AQUI" \
  https://keen-essence-production.up.railway.app/api/run-daily-cycle
```

Reemplaza `TU_CRON_SECRET_AQUI` con el CRON_SECRET que configuraste en Railway.

Deberías ver el resumen completo de la ejecución.

---

## 🎯 Recomendación de Horario

Te recomiendo configurar el cron para:
- **9 AM UTC** (3-4 AM hora México/US) → `0 9 * * *`
  
¿Por qué?
- Opinion.trade suele tener eventos nuevos por la mañana
- Los mercados financieros ya están activos
- Evitas competir con otros traders durante horas pico

---

## ⚠️ Recordatorios Importantes

### Modo TEST está activo:
- Límite: **$5 por día** entre las 5 IA
- Si se alcanza el límite, el sistema se detiene automáticamente
- Balance total: **$50** iniciales

### Para monitorear:
- Revisa el frontend: https://gentle-ambition-production.up.railway.app/
- Verás las predicciones actualizadas después de cada ejecución
- La tabla "The Contestants" mostrará el rendimiento de cada IA

---

## 🆘 Solución de Problemas

**El cron job no se ejecuta:**
- Verifica que la expresión cron sea correcta en https://crontab.guru
- Asegúrate de que el servicio esté desplegado (deployment successful)
- Revisa que SYSTEM_ENABLED=true esté en las variables

**El cron job falla:**
- Ve a los logs del servicio cron
- Busca el error específico
- Verifica que TODAS las API keys estén configuradas

**No veo predicciones nuevas:**
- Es normal si no hay eventos disponibles en Opinion.trade
- El sistema omite apuestas si no hay oportunidades con suficiente confianza
- Revisa los logs para ver qué analizó cada IA

---

## ✅ Checklist Final

Antes de dar por terminado:
- [ ] Servicio cron creado en Railway
- [ ] Variables de entorno copiadas
- [ ] Expresión cron configurada
- [ ] Start command configurado: `python run_daily_cycle.py`
- [ ] Deployment successful ✅
- [ ] Probado manualmente (ejecuta `python run_daily_cycle.py`)
- [ ] Frontend muestra predicciones

---

**¿Listo para activarlo? Sigue los pasos de la OPCIÓN 1 y avísame si necesitas ayuda.** 🚀
