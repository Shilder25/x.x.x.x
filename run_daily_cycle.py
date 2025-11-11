#!/usr/bin/env python3
"""
Railway Cron Job: Ejecuta el ciclo diario de predicciones de las 5 IA.

Este script se ejecuta una vez al día mediante Railway Cron Jobs.
IMPORTANTE: Debe salir inmediatamente después de completar para no consumir recursos.
"""

import os
import sys
from datetime import datetime
from database import TradingDatabase
from autonomous_engine import AutonomousEngine

def main():
    """
    Ejecuta el ciclo diario completo y sale inmediatamente.
    """
    start_time = datetime.now()
    print(f"\n{'='*70}")
    print(f"🤖 INICIO DEL CICLO DIARIO DE PREDICCIONES - {start_time.isoformat()}")
    print(f"{'='*70}\n")
    
    # Verificar que el sistema esté habilitado
    system_enabled = os.environ.get('SYSTEM_ENABLED', 'false').lower() == 'true'
    bankroll_mode = os.environ.get('BANKROLL_MODE', 'TEST').upper()
    
    print(f"📊 Configuración del Sistema:")
    print(f"   - Sistema Habilitado: {system_enabled}")
    print(f"   - Modo de Bankroll: {bankroll_mode}")
    print()
    
    if not system_enabled:
        print("⚠️  Sistema deshabilitado (SYSTEM_ENABLED=false)")
        print("   No se ejecutarán predicciones.")
        print(f"\n{'='*70}")
        sys.exit(0)
    
    db = None
    try:
        # Inicializar base de datos y motor autónomo
        print("🔧 Inicializando sistema...")
        db = TradingDatabase()
        engine = AutonomousEngine(db)
        
        # Ejecutar ciclo diario
        print("🚀 Ejecutando ciclo de predicciones...\n")
        results = engine.run_daily_cycle()
        
        # Mostrar resumen de resultados
        print(f"\n{'='*70}")
        print("📈 RESUMEN DEL CICLO:")
        print(f"{'='*70}")
        print(f"✓ Estado: {results.get('status', 'completed')}")
        print(f"✓ Timestamp: {results.get('timestamp')}")
        print(f"✓ Apuestas realizadas: {results.get('total_bets_placed', 0)}")
        print(f"✓ Apuestas omitidas: {results.get('total_bets_skipped', 0)}")
        print(f"✓ Categorías analizadas: {len(results.get('categories_analyzed', []))}")
        
        # Mostrar resultados por firma
        firms_results = results.get('firms_results', {})
        if firms_results:
            print(f"\n🤖 Resultados por IA:")
            for firm_name, firm_result in firms_results.items():
                print(f"   - {firm_name}:")
                print(f"     Eventos analizados: {firm_result.get('events_analyzed', 0)}")
                print(f"     Apuestas: {firm_result.get('bets_placed', 0)}")
                if firm_result.get('bet_amount'):
                    print(f"     Cantidad apostada: ${firm_result.get('bet_amount', 0):.2f}")
        
        # Mostrar errores si los hay
        errors = results.get('errors', [])
        if errors:
            print(f"\n⚠️  Errores encontrados: {len(errors)}")
            for i, error in enumerate(errors[:5], 1):  # Mostrar solo primeros 5
                print(f"   {i}. {error}")
        
        print(f"\n{'='*70}")
        
        # Calcular duración
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Ciclo completado en {duration:.2f} segundos")
        print(f"{'='*70}\n")
        
        # Salir exitosamente
        sys.exit(0)
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERROR CRÍTICO durante el ciclo:")
        print(f"{'='*70}")
        print(f"{type(e).__name__}: {str(e)}")
        
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        
        print(f"\n{'='*70}\n")
        
        # Salir con error
        sys.exit(1)
        
    finally:
        # Garantizar cierre de conexiones incluso si hay excepciones
        if db:
            print("\n🔒 Cerrando conexiones...")
            try:
                db.close()
            except Exception as e:
                print(f"⚠️  Error al cerrar base de datos: {e}")

if __name__ == "__main__":
    main()
