# ⚠️ Problema: Opinion.trade API Geo-Bloqueada

## 🔍 Diagnóstico

El sistema actualmente **NO PUEDE** acceder a la API de Opinion.trade debido a un bloqueo geográfico activo por parte de Opinion.trade.

### Error Encontrado
```
API error 10403
Mensaje: Invalid area
```

### Causa Raíz
Opinion.trade está bloqueando **TODAS** las solicitudes API programáticas, independientemente de la región desde donde se hagan. Esto incluye:
- ❌ Replit (US East)
- ❌ Railway EU West (Amsterdam)
- ❌ Cualquier otra región

## 📋 Lo Que Hemos Verificado

✅ **SDK configurado correctamente**: opinion-clob-sdk v0.2.5 con todos los parámetros necesarios
✅ **Credenciales válidas**: API key y Private Key funcionan para la inicialización
✅ **Región correcta**: Railway desplegado en EU West (Amsterdam)
✅ **Código sin errores**: La llamada `client.get_markets()` usa parámetros correctos

❌ **El bloqueo viene del backend de Opinion.trade**, no de nuestro código

---

## 🎯 Solución Requerida: Contactar a Opinion.trade

**Acción obligatoria:** Debes solicitar a Opinion.trade que permita (whitelist) las IPs de tu deployment de Railway.

### Pasos a Seguir

### 1. Obtener las IPs de Salida de Railway

Railway usa IPs dinámicas. Necesitas obtener las IPs de salida de tu deployment:

**Opción A: Desde Railway Dashboard**
1. Ve a tu proyecto en Railway
2. Settings → Networking → Outbound IPs
3. Copia todas las IPs listadas

**Opción B: Verificar desde el deployment**
Agrega un endpoint temporal en `api.py`:
```python
@app.route('/api/my-ip', methods=['GET'])
def get_my_ip():
    import requests
    try:
        ip = requests.get('https://api.ipify.org').text
        return jsonify({'ip': ip})
    except:
        return jsonify({'error': 'Could not get IP'}), 500
```

Luego visita: `https://keen-essence-production.up.railway.app/api/my-ip`

---

### 2. Contactar a Opinion.trade

**Información de contacto:**
- Email de soporte (busca en su sitio web)
- Discord oficial de Opinion.trade
- Telegram grupo oficial

**Mensaje sugerido (en inglés):**

```
Subject: API Access Request - Error 10403 "Invalid area"

Hello Opinion.trade Team,

I am developing an AI-powered prediction market trading system that uses your API 
via the opinion-clob-sdk (v0.2.5) on BNB Chain mainnet.

Currently, I am receiving error code 10403 with message "Invalid area" when calling 
get_markets() and other API endpoints.

My deployment details:
- Hosting: Railway (https://railway.app)
- Region: EU West (Amsterdam)
- Outbound IPs: [LISTA TUS IPs AQUÍ]
- API Key: [TUS PRIMEROS 8 CARACTERES DEL API KEY]
- Wallet Address: 0x43C9bAd451ed65b5268cec681FCe42AdA00Fc675

Could you please:
1. Whitelist the IP addresses above for API access
2. Confirm if there are any additional requirements or restrictions
3. Provide the correct API endpoint if different from https://proxy.opinion.trade:8443

Thank you for your assistance!

Best regards,
[Tu Nombre]
```

---

### 3. Información para Proporcionar

Cuando contactes a Opinion.trade, ten lista esta información:

| Campo | Valor |
|-------|-------|
| **SDK Version** | opinion-clob-sdk v0.2.5 |
| **Chain ID** | 56 (BNB Chain Mainnet) |
| **API Host** | https://proxy.opinion.trade:8443 |
| **Wallet Address** | 0x43C9bAd451ed65b5268cec681FCe42AdA00Fc675 |
| **Deployment Region** | EU West (Amsterdam, Railway) |
| **Error Code** | 10403 |
| **Error Message** | Invalid area |

---

## 🔧 Verificación de Acceso Restaurado

Una vez que Opinion.trade confirme que han permitido tus IPs, ejecuta:

```bash
# Desde Railway deployment (no desde Replit)
python test_autonomous_system.py
```

La Prueba 2 debería pasar:
```
✓ PASÓ │ Obtención de eventos
```

---

## 🛠️ Plan de Contingencia

Si Opinion.trade no responde o rechaza la solicitud:

### Opción 1: Usar un Proxy Regional
Configurar un proxy en una región permitida (si identificas una)

### Opción 2: Modo Simulación Completo
Implementar un sistema de simulación que no use la API real:
- Generar eventos ficticios para pruebas
- Simular respuestas de la API
- Permitir que el sistema funcione sin conexión real

### Opción 3: Plataforma Alternativa
Considerar usar otras plataformas de predicción de mercados:
- Polymarket (usa py-clob-client)
- Otras plataformas CLOB en BNB Chain

---

## 📊 Estado Actual del Sistema

| Componente | Estado |
|------------|--------|
| Frontend (Railway) | ✅ Funcionando |
| Backend API (Railway) | ✅ Funcionando |
| Base de Datos | ✅ Funcionando |
| LLM Integraciones | ✅ Funcionando |
| **Opinion.trade API** | ❌ **BLOQUEADA** |
| Autonomous Engine | ⏸️ En espera de API |
| Daily Cron Job | ⏸️ En espera de API |

**El sistema está 90% completo**. Solo falta resolver el acceso a Opinion.trade API.

---

## ⏱️ Tiempo Estimado de Resolución

- **Mejor caso**: 1-3 días (Opinion.trade responde y permite IPs)
- **Caso promedio**: 1-2 semanas (comunicación y verificaciones)
- **Peor caso**: Implementar plan de contingencia

---

## 🔗 Referencias

- **Opinion.trade Website**: https://opinion.trade
- **SDK en uso**: https://pypi.org/project/opinion-clob-sdk/
- **BNB Chain Docs**: https://docs.bnbchain.org/

---

**Última actualización**: Noviembre 2025  
**Estado**: Esperando respuesta de Opinion.trade
