# 🚀 INSTRUCCIONES PARA PUBLICAR - TradingAgents

## ⚠️ IMPORTANTE: Cambiar Configuración de Deployment

El proyecto ha migrado de Streamlit a React/Next.js + Flask. **Debes actualizar la configuración de deployment antes de publicar.**

## 📋 Pasos para Publicar Correctamente

### Paso 1: Abrir la Configuración de Deployment

1. Haz clic en el botón **"Deploy"** o **"Publish"** en la parte superior derecha de Replit
2. Se abrirá el panel de deployment/publishing

### Paso 2: Editar el Run Command

Busca la sección que dice **"Run command"** o **"Comando de ejecución"**

**CAMBIAR DE:**
```
streamlit run app.py --server.port 5000
```

**A UNO DE ESTOS DOS:**

**Opción 1 (Recomendado - Más simple):**
```
python app.py
```

**Opción 2 (Alternativo):**
```
python main.py
```

### Paso 3: Verificar la Configuración de Puerto

Asegúrate que el **puerto 5000** esté configurado como el puerto principal (webview/HTTP port)

### Paso 4: Guardar y Desplegar

1. Guarda los cambios en la configuración
2. Haz clic en "Deploy" o "Publish"
3. Espera a que termine el deployment (puede tardar 2-3 minutos)

---

## ✅ Qué Deberías Ver Después del Deployment

Si todo funcionó correctamente, verás:

✓ Interfaz de React/Next.js con diseño Alpha Arena  
✓ BORDES NEGROS (2px) en todas las secciones  
✓ Header con precios de crypto (BTC, ETH, SOL, BNB, DOGE, XRP)  
✓ Navegación horizontal: LIVE | LEADERBOARD | BLOG | MODELS  
✓ Gráfico de rendimiento con líneas de colores vibrantes  
✓ Tablas con datos de las AIs  

## ❌ Qué NO Deberías Ver

Si ves esto, el deployment aún está mal configurado:

✗ Código HTML mostrándose como texto plano  
✗ Menú de Streamlit (Rerun, Settings, Print, Record a screencast)  
✗ Errores sobre "app.py not found" o "streamlit not found"  
✗ Pantalla en blanco o error 404  

---

## 🔧 Si el Deployment Falla

### Error: "streamlit: command not found"
**Solución:** Cambia el run command a `python app.py` (sin "streamlit run")

### Error: "File does not exist: app.py"
**Solución:** Verifica que el archivo `app.py` existe en el directorio raíz (existe desde Nov 9, 2025)

### Error: "Module 'main' not found"
**Solución:** Verifica que `main.py` existe en el directorio raíz

### El deployment se ejecuta pero no veo la interfaz
**Solución:** 
1. Verifica que el puerto 5000 esté configurado como webview
2. Revisa los logs del deployment para ver si hay errores
3. Asegúrate que ambos servicios (Flask y Next.js) se iniciaron correctamente

---

## 🏗️ Arquitectura del Proyecto

```
Deployment Entry Point: app.py
         ↓
    Llama a: main.py
         ↓
    Inicia:
    ├─ Flask API (puerto 8000) - Backend
    └─ Next.js Frontend (puerto 5000) - UI Principal
```

El puerto 5000 (Next.js) es el que verán los usuarios.  
El puerto 8000 (Flask) es usado internamente por Next.js para obtener datos.

---

## 📞 Problemas Persistentes

Si después de seguir todos estos pasos todavía tienes problemas:

1. Verifica que los archivos `app.py` y `main.py` existen
2. Revisa los logs del deployment para errores específicos
3. Asegúrate de haber guardado la configuración del run command
4. Intenta hacer un "Clear cache and redeploy" si está disponible

---

## 🎯 Checklist Final Antes de Publicar

- [ ] Cambié el run command de "streamlit run app.py" a "python app.py"
- [ ] El puerto 5000 está configurado como webview
- [ ] Guardé la configuración de deployment
- [ ] Los archivos app.py y main.py existen en el proyecto
- [ ] Los workflows "api" y "frontend" funcionan correctamente en desarrollo

Si todos los checkboxes están marcados, ¡estás listo para publicar! 🚀
