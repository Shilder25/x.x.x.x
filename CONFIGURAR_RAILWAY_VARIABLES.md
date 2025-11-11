# 🔑 Configurar Variables de Entorno en Railway

## ¿Por qué necesito hacer esto?

El sistema autónomo necesita las API keys para funcionar. En Replit ya las tienes configuradas, pero Railway es un servidor separado y necesita su propia copia de estas claves.

---

## 📝 Pasos EXACTOS (5 minutos):

### 1️⃣ Abre Railway en tu navegador

Ve a: https://railway.app → Tu proyecto → Servicio **"keen-essence"** (el backend, NO el frontend)

### 2️⃣ Haz click en la pestaña "Variables" (arriba)

### 3️⃣ Click en "New Variable" (botón azul)

### 4️⃣ Copia TODAS estas variables de Replit a Railway

**En Replit:** Busca el ícono de candado 🔒 "Secrets" en la barra lateral izquierda.

**Agrega estas variables EN RAILWAY una por una:**

**Lista completa (copia EXACTAMENTE estos nombres):**

```plaintext
OPINION_TRADE_API_KEY
OPINION_WALLET_PRIVATE_KEY
ALPHA_VANTAGE_API_KEY
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
DEEPSEEK_API_KEY
QWEN_API_KEY
XAI_API_KEY
AI_INTEGRATIONS_OPENAI_API_KEY
AI_INTEGRATIONS_OPENAI_BASE_URL
AI_INTEGRATIONS_GEMINI_API_KEY
AI_INTEGRATIONS_GEMINI_BASE_URL
BANKROLL_MODE
SYSTEM_ENABLED
```

**Cómo hacerlo:**
1. En Replit: Abre "Secrets" (ícono de candado 🔒)
2. Copia el NOMBRE de la variable (ejemplo: `OPINION_TRADE_API_KEY`)
3. Copia el VALOR de la variable (el texto largo)
4. En Railway: Click "New Variable", pega nombre y valor
5. Repite para TODAS las variables de arriba

**⚠️ IMPORTANTE - Estas dos variables las escribes TÚ (no están en Replit):**

```
BANKROLL_MODE = TEST
SYSTEM_ENABLED = true
```

- **BANKROLL_MODE = TEST** → Modo seguro: $50 total, $5/día máximo
- **SYSTEM_ENABLED = true** → Activa el sistema autónomo

---

### 5️⃣ IMPORTANTE: Haz click en "Deploy" después de agregar todas las variables

Railway **NO despliega automáticamente** los cambios. Después de agregar TODAS las variables:
1. Busca el botón **"Deploy"** o **"Review Changes"** 
2. Haz click para aplicar los cambios
3. Railway redesplegará el backend (espera 2-3 minutos)
4. Verás "Deployment successful" ✅ cuando termine

---

## ⚠️ MUY IMPORTANTE:

### `BANKROLL_MODE = TEST`
Modo seguro para pruebas:
- **$50 inicial** en total para las 5 IA
- **$5 máximo por día** (límite diario combinado)
- Protección contra pérdidas grandes

### `SYSTEM_ENABLED = true`
Activa el motor autónomo. Si lo dejas en `false`, las IA NO harán predicciones.

---

## ✅ ¿Cómo verificar que funcionó?

Después del despliegue:
1. Ve a la pestaña **"Deployments"** en Railway
2. Verás "Deployment successful" ✅
3. Haz click en **"View Logs"** para ver si aparece:
   ```
   ✓ Opinion.trade SDK initialized (wallet: 0x43C9...)
   [BANKROLL MODE] TEST - Initial: $50, Daily limit: $5
   ```

Si ves esos mensajes, ¡todo está configurado correctamente!

---

## 🆘 Si tienes problemas:

**No encuentro los Secrets en Replit:**
- Busca el ícono de candado 🔒 en la barra lateral izquierda de Replit
- O ve a Tools → Secrets

**Railway no guarda las variables:**
- Asegúrate de hacer click en "Add" después de pegar cada una
- Verifica que estás en el servicio "keen-essence" (backend), NO en "gentle-ambition" (frontend)

---

**Una vez que hayas agregado TODAS las variables en Railway, avísame y probaremos el sistema** 🚀

Esto tomará unos 5 minutos. ¿Necesitas ayuda con algo específico mientras lo haces?
