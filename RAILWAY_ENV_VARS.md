# 🔐 Railway Environment Variables - Quick Reference

Esta es una lista completa de todas las variables de entorno que necesitas configurar en Railway.

---

## 📦 Backend Service (`api`)

Configura estas 15 variables en el servicio **api**:

### LLM API Keys (5 variables)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `AI_INTEGRATIONS_OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `AI_INTEGRATIONS_OPENAI_BASE_URL` | OpenAI base URL | `https://api.openai.com/v1` |
| `DEEPSEEK_API_KEY` | Deepseek LLM API key | `sk-...` |
| `QWEN_API_KEY` | Qwen LLM API key | `sk-...` |
| `XAI_API_KEY` | Grok (XAI) API key | `xai-...` |

### Financial Data APIs (2 variables)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage para datos técnicos | `ABC123...` |
| `OPINION_TRADE_API_KEY` | Opinion.trade API key | `ot_...` |

### Reddit API (2 variables)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit app client ID | `abc123...` |
| `REDDIT_CLIENT_SECRET` | Reddit app secret | `xyz456...` |

### Trading Wallet (1 variable - CRÍTICA) ⚠️

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `OPINION_WALLET_PRIVATE_KEY` | BNB Chain wallet private key | `0x1234abcd...` |

**⚠️ IMPORTANTE**: 
- Esta es tu clave privada de blockchain
- Nunca la compartas públicamente
- Asegúrate de que la wallet tenga fondos suficientes (USDT en BNB Chain)

### Sistema de Control (3 variables)

| Variable | Descripción | Valores posibles |
|----------|-------------|------------------|
| `ADMIN_PASSWORD` | Password para admin dashboard | Tu password seguro |
| `BANKROLL_MODE` | Modo de trading | `TEST` o `PRODUCTION` |
| `SYSTEM_ENABLED` | Sistema on/off | `true` o `false` |

**Recomendado para inicio**: 
- `BANKROLL_MODE=TEST` (límite $5/día)
- `SYSTEM_ENABLED=true`

### Railway-Specific (2 variables)

| Variable | Descripción | Valor |
|----------|-------------|-------|
| `PORT` | Puerto del backend | `8000` |
| `PYTHONUNBUFFERED` | Logs sin buffer | `1` |

---

## 🌐 Frontend Service (`frontend`)

Configura estas 2 variables en el servicio **frontend**:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | URL pública del backend API | `https://api-production.up.railway.app` |
| `PORT` | Puerto del frontend | `5000` |

**⚠️ IMPORTANTE**: 
Reemplaza `https://api-production.up.railway.app` con la URL real que Railway asignó a tu servicio `api`.

Para obtener esta URL:
1. Ve al servicio `api` en Railway
2. Click en **Settings → Networking**
3. Copia el **Public Domain** (ej: `api-production-abc123.up.railway.app`)
4. Úsala con `https://` prefijo

---

## ✅ Checklist de Configuración

Marca cada variable conforme la configures:

### Backend (`api`)
- [ ] `AI_INTEGRATIONS_OPENAI_API_KEY`
- [ ] `AI_INTEGRATIONS_OPENAI_BASE_URL`
- [ ] `DEEPSEEK_API_KEY`
- [ ] `QWEN_API_KEY`
- [ ] `XAI_API_KEY`
- [ ] `ALPHA_VANTAGE_API_KEY`
- [ ] `OPINION_TRADE_API_KEY`
- [ ] `REDDIT_CLIENT_ID`
- [ ] `REDDIT_CLIENT_SECRET`
- [ ] `OPINION_WALLET_PRIVATE_KEY` ⚠️
- [ ] `ADMIN_PASSWORD`
- [ ] `BANKROLL_MODE` (set to `TEST`)
- [ ] `SYSTEM_ENABLED` (set to `true`)
- [ ] `PORT` (set to `8000`)
- [ ] `PYTHONUNBUFFERED` (set to `1`)

### Frontend (`frontend`)
- [ ] `NEXT_PUBLIC_API_URL` (URL del servicio api)
- [ ] `PORT` (set to `5000`)

**Total: 17 variables**

---

## 🔄 Cómo Obtener tus API Keys

Si no tienes alguna de estas keys:

### OpenAI
1. https://platform.openai.com/api-keys
2. Create new secret key

### Deepseek
1. https://platform.deepseek.com
2. API Keys section

### Qwen (Alibaba Cloud)
1. https://dashscope.console.aliyun.com
2. API Key Management

### XAI (Grok)
1. https://console.x.ai
2. API Keys

### Alpha Vantage
1. https://www.alphavantage.co/support/#api-key
2. Free tier disponible

### Opinion.trade
1. https://app.opinion.trade
2. Settings → API Keys

### Reddit
1. https://www.reddit.com/prefs/apps
2. Create app (script type)
3. Usa client ID y secret

### BNB Chain Wallet
Opciones:
1. **MetaMask**: Exporta private key desde Settings
2. **Trust Wallet**: Revela private key en wallet settings
3. **Nuevo wallet**: Usa `eth-account` para generar:
   ```python
   from eth_account import Account
   account = Account.create()
   print(f"Address: {account.address}")
   print(f"Private Key: {account.key.hex()}")
   ```

**⚠️ Fondos necesarios**: La wallet debe tener USDT en BNB Chain para trading.

---

## 🔒 Seguridad

### Mejores Prácticas

✅ **DO**:
- Usa variables de entorno en Railway (no hardcodees)
- Mantén `OPINION_WALLET_PRIVATE_KEY` solo en Railway (nunca en código)
- Usa `BANKROLL_MODE=TEST` hasta estar 100% seguro
- Cambia `ADMIN_PASSWORD` regularmente
- Revisa logs para detectar uso sospechoso

❌ **DON'T**:
- Nunca subas keys a GitHub/repositorio público
- Nunca compartas tu `OPINION_WALLET_PRIVATE_KEY`
- No uses la misma wallet para trading y fondos grandes
- No pongas `SYSTEM_ENABLED=true` sin supervisión inicial

### Wallet Dedicada

**Recomendado**: Usa una wallet dedicada solo para este proyecto:
- Fondos limitados ($50-100 para TEST mode)
- Fácil de monitorear
- Menor riesgo si hay bug o compromiso

---

## 🧪 Testing de Variables

Después de configurar, verifica que funcionan:

### Test 1: Backend Health
```bash
curl https://TU-API-URL.railway.app/health
```
Debe mostrar todas las keys como "configured" ✅

### Test 2: LLMs
```bash
curl https://TU-API-URL.railway.app/api/firms
```
Debe listar 5 firms (ChatGPT, Gemini, Qwen, Deepseek, Grok)

### Test 3: Opinion.trade
```bash
curl https://TU-API-URL.railway.app/api/markets
```
Debe listar mercados reales (no error 10403)

---

## 📝 Plantilla para Copiar/Pegar

Usa esto en Railway (reemplaza valores reales):

```bash
# LLM APIs
AI_INTEGRATIONS_OPENAI_API_KEY=sk-proj-XXXXXX
AI_INTEGRATIONS_OPENAI_BASE_URL=https://api.openai.com/v1
DEEPSEEK_API_KEY=sk-XXXXXX
QWEN_API_KEY=sk-XXXXXX
XAI_API_KEY=xai-XXXXXX

# Financial Data
ALPHA_VANTAGE_API_KEY=XXXXXX
OPINION_TRADE_API_KEY=ot_XXXXXX

# Reddit
REDDIT_CLIENT_ID=XXXXXX
REDDIT_CLIENT_SECRET=XXXXXX

# Trading Wallet
OPINION_WALLET_PRIVATE_KEY=0xXXXXXX

# Sistema
ADMIN_PASSWORD=tu_password_seguro
BANKROLL_MODE=TEST
SYSTEM_ENABLED=true

# Railway
PORT=8000
PYTHONUNBUFFERED=1
```

---

## ❓ FAQ

**P: ¿Qué pasa si no configuro una variable?**
R: El sistema puede fallar al inicio o esa funcionalidad no trabajará. Revisa logs para ver errores específicos.

**P: ¿Puedo usar las mismas keys de Replit?**
R: Sí, copia exactamente las mismas variables que usas actualmente.

**P: ¿Qué hago si no tengo alguna API key?**
R: Sigue la sección "Cómo Obtener tus API Keys" arriba. Algunas tienen tier gratuito.

**P: ¿Es seguro poner la private key en Railway?**
R: Sí, Railway encripta todas las variables de entorno. Es más seguro que tenerla en código.

**P: ¿Cuánto cuesta mantener estas APIs?**
R: Depende del uso. Para testing, la mayoría tienen tier gratuito suficiente.

---

**¿Listo?** Copia esta lista y configura cada variable en Railway Dashboard. ✅
