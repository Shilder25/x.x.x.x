#!/usr/bin/env python3
"""
Health Check Script para Opinion.trade API
Verifica si el acceso a Opinion.trade ha sido restaurado
"""

import os
from datetime import datetime
from opinion_trade_api import OpinionTradeAPI

def print_header():
    print("\n" + "="*70)
    print(" VERIFICACIÓN DE SALUD - OPINION.TRADE API")
    print("="*70 + "\n")

def print_section(title):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}\n")

def check_api_connectivity():
    """Verifica conectividad básica con Opinion.trade"""
    print_header()
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"🌍 Modo: {os.environ.get('BANKROLL_MODE', 'TEST')}")
    print(f"⚙️  Sistema: {'Habilitado' if os.environ.get('SYSTEM_ENABLED', 'false').lower() == 'true' else 'Deshabilitado'}")
    
    # Test 1: Inicialización
    print_section("Test 1: Inicialización del Cliente")
    try:
        api = OpinionTradeAPI()
        
        if not api.client:
            print("❌ ERROR: Cliente no inicializado")
            print("   Verifica las variables de entorno:")
            print("   - OPINION_TRADE_API_KEY")
            print("   - OPINION_WALLET_PRIVATE_KEY")
            return False
        
        print(f"✅ Cliente inicializado correctamente")
        print(f"   Wallet: {api.wallet_address}")
        print(f"   API Key: {'Configurado' if api.api_key else 'No configurado'}")
        
    except Exception as e:
        print(f"❌ ERROR durante inicialización: {str(e)}")
        return False
    
    # Test 2: Acceso a API
    print_section("Test 2: Acceso a get_markets()")
    try:
        result = api.get_available_events(limit=1)
        
        if result.get('success'):
            print("✅ ÉXITO: API de Opinion.trade respondió correctamente")
            print(f"   Eventos disponibles: {result.get('count', 0)}")
            
            if result.get('events'):
                event = result['events'][0]
                print(f"\n   Primer evento:")
                print(f"   - Título: {event.get('title')}")
                print(f"   - ID: {event.get('event_id')}")
                print(f"   - Categoría: {event.get('category')}")
            
            return True
        else:
            error_code = result.get('error')
            error_msg = result.get('message')
            
            print(f"❌ ERROR: {error_code}")
            print(f"   Mensaje: {error_msg}")
            
            # Analizar tipo de error
            if "10403" in str(error_code) or "Invalid area" in str(error_msg):
                print("\n⚠️  GEO-BLOQUEO ACTIVO")
                print("   Opinion.trade sigue bloqueando el acceso.")
                print("   ")
                print("   Pasos a seguir:")
                print("   1. Verifica que Opinion.trade haya whitelistado tus IPs")
                print("   2. Contacta al soporte de Opinion.trade si aún no lo has hecho")
                print("   3. Proporciona las IPs de salida de Railway")
                print("   ")
                print("   📄 Ver: PROBLEMA_OPINION_TRADE_GEO_BLOCK.md para más detalles")
            elif "credentials" in str(error_msg).lower() or "auth" in str(error_msg).lower():
                print("\n⚠️  PROBLEMA DE CREDENCIALES")
                print("   Verifica que tu API key sea válida.")
            else:
                print("\n⚠️  ERROR DESCONOCIDO")
                print("   Este es un error diferente al geo-bloqueo.")
            
            return False
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {str(e)}")
        import traceback
        print("\nTraceback:")
        traceback.print_exc()
        return False
    
def main():
    """Ejecutar verificación de salud"""
    success = check_api_connectivity()
    
    # Resumen final
    print("\n" + "="*70)
    if success:
        print("✅ ESTADO: Opinion.trade API ACCESIBLE")
        print("\nEl sistema está listo para ejecutar predicciones autónomas.")
        print("Puedes proceder a activar el cron job en Railway.")
    else:
        print("❌ ESTADO: Opinion.trade API BLOQUEADA")
        print("\nEl sistema NO puede ejecutar predicciones hasta que se resuelva el acceso.")
        print("\n📖 Consulta PROBLEMA_OPINION_TRADE_GEO_BLOCK.md para instrucciones detalladas")
        print("   sobre cómo contactar a Opinion.trade y solicitar whitelist de IPs.")
    print("="*70 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
