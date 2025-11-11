#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema autónomo funciona correctamente.
Prueba conexión a Opinion.trade y generación de predicciones sin hacer apuestas reales.
"""

import os
import sys
from datetime import datetime
from opinion_trade_api import OpinionTradeAPI
from llm_clients import FirmOrchestrator
from database import TradingDatabase

def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def test_opinion_trade_connection():
    """Prueba 1: Verificar conexión a Opinion.trade"""
    print_section("PRUEBA 1: Conexión a Opinion.trade")
    
    api = OpinionTradeAPI()
    
    print(f"✓ API Key configurada: {'Sí' if api.api_key else 'No'}")
    print(f"✓ Private Key configurada: {'Sí' if api.private_key else 'No'}")
    print(f"✓ Wallet Address: {api.wallet_address if api.wallet_address else 'No disponible'}")
    print(f"✓ Cliente inicializado: {'Sí' if api.client else 'No'}")
    
    if not api.client:
        print("\n❌ ERROR: Cliente no inicializado. Verifica las API keys.")
        return False
    
    print("\n✓ Conexión a Opinion.trade exitosa")
    return True

def test_fetch_events():
    """Prueba 2: Obtener eventos disponibles"""
    print_section("PRUEBA 2: Obtener Eventos de Opinion.trade")
    
    api = OpinionTradeAPI()
    result = api.get_available_events(limit=5)
    
    if not result.get('success'):
        print(f"❌ ERROR: {result.get('error')}")
        print(f"   Mensaje: {result.get('message')}")
        return False, []
    
    events = result.get('events', [])
    print(f"✓ Eventos obtenidos: {len(events)}")
    
    if events:
        print("\nPrimeros 3 eventos disponibles:")
        for i, event in enumerate(events[:3], 1):
            print(f"\n{i}. {event.get('title', 'Sin título')}")
            print(f"   ID: {event.get('event_id')}")
            print(f"   Categoría: {event.get('category', 'Unknown')}")
            print(f"   Estado: {event.get('status')}")
    else:
        print("\n⚠️  No hay eventos disponibles en este momento")
    
    return True, events

def test_ai_prediction(event):
    """Prueba 3: Generar predicción de una IA"""
    print_section("PRUEBA 3: Generación de Predicción por ChatGPT")
    
    orchestrator = FirmOrchestrator()
    
    # Crear prompt simple para prueba
    test_prompt = f"""
Analiza este evento de predicción y proporciona tu análisis:

EVENTO: {event.get('title')}
DESCRIPCIÓN: {event.get('description', 'No disponible')}
CATEGORÍA: {event.get('category', 'Unknown')}

Proporciona:
1. Tu predicción (YES/NO)
2. Nivel de confianza (0-100)
3. Razón breve
"""
    
    print(f"Evento a analizar: {event.get('title')}")
    print("\nGenerando predicción con ChatGPT...")
    
    try:
        response = orchestrator.generate_prediction("ChatGPT", test_prompt)
        
        print(f"\n✓ Predicción generada exitosamente")
        print(f"\nRespuesta de la IA:")
        print("-" * 60)
        print(response[:500] + "..." if len(response) > 500 else response)
        print("-" * 60)
        
        return True
    except Exception as e:
        print(f"\n❌ ERROR al generar predicción: {str(e)}")
        return False

def test_database():
    """Prueba 4: Verificar base de datos"""
    print_section("PRUEBA 4: Verificación de Base de Datos")
    
    try:
        db = TradingDatabase()
        
        # Verificar firmas existentes
        firms = db.get_all_firm_performance()
        print(f"✓ Firmas registradas: {len(firms)}")
        
        if firms:
            print("\nRendimiento actual de las IA:")
            for firm in firms:
                print(f"  - {firm['firm_name']}: {firm['total_predictions']} predicciones, "
                      f"${firm.get('current_balance', 0):.2f} balance")
        
        return True
    except Exception as e:
        print(f"❌ ERROR de base de datos: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   PRUEBA DEL SISTEMA AUTÓNOMO DE TRADING CON IA           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Verificar modo de operación
    bankroll_mode = os.environ.get('BANKROLL_MODE', 'TEST').upper()
    system_enabled = os.environ.get('SYSTEM_ENABLED', 'false').lower() == 'true'
    
    print(f"\nModo de Operación: {bankroll_mode}")
    print(f"Sistema Habilitado: {'Sí' if system_enabled else 'No'}")
    
    if not system_enabled:
        print("\n⚠️  ADVERTENCIA: SYSTEM_ENABLED=false - El sistema no ejecutará apuestas")
        print("   Para activarlo, configura SYSTEM_ENABLED=true en las variables de entorno")
    
    # Ejecutar pruebas
    results = []
    
    # Prueba 1: Conexión
    test1_ok = test_opinion_trade_connection()
    results.append(("Conexión a Opinion.trade", test1_ok))
    
    if not test1_ok:
        print("\n❌ No se puede continuar sin conexión a Opinion.trade")
        sys.exit(1)
    
    # Prueba 2: Eventos
    test2_ok, events = test_fetch_events()
    results.append(("Obtención de eventos", test2_ok))
    
    # Prueba 3: Predicción de IA (solo si hay eventos)
    if test2_ok and events:
        test3_ok = test_ai_prediction(events[0])
        results.append(("Predicción de IA", test3_ok))
    else:
        print_section("PRUEBA 3: Omitida (no hay eventos)")
        results.append(("Predicción de IA", None))
    
    # Prueba 4: Base de datos
    test4_ok = test_database()
    results.append(("Base de datos", test4_ok))
    
    # Resumen final
    print_section("RESUMEN DE PRUEBAS")
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASÓ"
        elif result is False:
            status = "✗ FALLÓ"
        else:
            status = "- OMITIDA"
        
        print(f"{status:12} │ {test_name}")
    
    # Resultado final
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    
    print(f"\n{'=' * 60}")
    if failed == 0:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("\nEl sistema está listo para ejecutar predicciones autónomas.")
        print("Usa: python autonomous_engine.py para ejecutar un ciclo completo.")
    else:
        print(f"⚠️  {failed} PRUEBA(S) FALLARON")
        print("\nRevisa los errores arriba y corrige la configuración.")
    
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    main()
