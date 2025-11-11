#!/bin/bash

echo "================================"
echo "Subiendo cambios a GitHub"
echo "================================"
echo ""

# Configurar git (reemplaza con tus datos)
echo "Paso 1: Configurando git..."
git config --global user.name "Tu Nombre Aquí"
git config --global user.email "tu-email@ejemplo.com"

echo "Paso 2: Agregando archivos modificados..."
git add .

echo "Paso 3: Creando commit..."
git commit -m "Fix: Disable ESLint rule to allow Railway deployment"

echo "Paso 4: Subiendo a GitHub..."
echo "IMPORTANTE: Cuando te pida Password, usa tu TOKEN de GitHub, NO tu contraseña"
git push origin main

echo ""
echo "================================"
echo "¡Listo! Revisa Railway para ver el despliegue automático"
echo "================================"
