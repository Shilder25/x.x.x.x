# Guía de Publicación (Deployment) - TradingAgents

## El Problema
Cuando haces clic en "Publish/Deploy" en Replit, el sistema está mostrando la vieja aplicación de Streamlit en lugar de la nueva interfaz de React/Next.js con diseño Alpha Arena.

## La Solución

### Paso 1: Configurar el Deployment en Replit

1. **Haz clic en el botón "Deploy"** en la parte superior derecha de Replit

2. **En la configuración de Deployment**, busca la sección de "Run Command" o "Comando de Ejecución"

3. **Cambia el comando** de:
   ```
   streamlit run app.py --server.port 5000
   ```
   
   A:
   ```
   python main.py
   ```
   
   **Nota:** `main.py` automáticamente:
   - ✅ Instala las dependencias de npm
   - ✅ Hace el build de producción de Next.js
   - ✅ Inicia Flask API en puerto 8000
   - ✅ Inicia Next.js en puerto 5000

4. **Configura el puerto principal**: Asegúrate de que el puerto **5000** esté configurado como el puerto web principal (webview)

5. **Guarda y despliega**

### Paso 2: Verificar el Deployment

Después de desplegar, deberías ver:
- ✅ Interfaz de React/Next.js con diseño Alpha Arena
- ✅ BORDES NEGROS (2px sólidos) en todas las secciones
- ✅ Header con precios de crypto en tiempo real
- ✅ Navegación: LIVE | LEADERBOARD | BLOG | MODELS
- ✅ Gráfico de rendimiento con líneas de colores vibrantes

**NO deberías ver:**
- ❌ Código HTML mostrándose como texto
- ❌ Menú de Streamlit (Rerun, Settings, Print)
- ❌ La vieja interfaz de Streamlit

### Arquitectura del Proyecto

```
Puerto 5000 (Frontend) ← Este es el puerto principal (webview)
  ↓
Next.js React App con diseño Alpha Arena
  ↓
Llama a → Puerto 8000 (Backend API)
           ↓
        Flask REST API
           ↓
        Datos de Python (database, LLMs, etc.)
```

### Archivos Importantes

- **frontend/**: Aplicación Next.js con diseño Alpha Arena
- **api.py**: API REST Flask que expone datos del backend
- **main.py**: Script que coordina ambos servicios para deployment
- **app_old_streamlit.py**: Archivo viejo renombrado (IGNORAR)
- **static_old_streamlit/**: Directorio viejo renombrado (IGNORAR)

### Workflows de Desarrollo

Durante el desarrollo en Replit, tenemos dos workflows:
- **api**: Ejecuta Flask API en puerto 8000
- **frontend**: Ejecuta Next.js dev server en puerto 5000

Estos workflows funcionan perfectamente para desarrollo local, pero para deployment necesitas usar el comando de `main.py` o el comando combinado.

### Problemas Comunes

**Problema:** Todavía veo la aplicación de Streamlit al publicar
- **Solución:** Verifica que el comando de deployment esté actualizado según el Paso 1

**Problema:** Error "Module not found" o "npm not found"
- **Solución:** Usa la Opción A (main.py) que maneja las dependencias automáticamente

**Problema:** El frontend se ve pero el API no responde
- **Solución:** Asegúrate de que ambos servicios (Flask y Next.js) estén iniciándose en el comando de deployment

### Soporte

Si después de seguir estos pasos todavía ves problemas, verifica:
1. Que el puerto 5000 esté configurado como webview
2. Que no haya errores en los logs del deployment
3. Que los archivos viejos de Streamlit estén renombrados (app_old_streamlit.py)
