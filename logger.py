import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

class AutonomousLogger:
    """
    Sistema de logging centralizado para el motor autónomo.
    Guarda logs en archivos rotativos y permite consulta vía API.
    """
    
    def __init__(self, log_dir: str = "logs", max_bytes: int = 10*1024*1024, backup_count: int = 5):
        """
        Args:
            log_dir: Directorio donde guardar logs
            max_bytes: Tamaño máximo de cada archivo de log (default: 10MB)
            backup_count: Número de archivos de respaldo a mantener
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Determinar nivel de logging desde env (default: INFO)
        log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        # Crear logger principal
        self.logger = logging.getLogger('autonomous_engine')
        self.logger.setLevel(logging.DEBUG)  # Logger acepta todos los niveles
        
        # Evitar duplicar handlers si ya existen
        if not self.logger.handlers:
            # Handler para archivo con rotación
            log_file = self.log_dir / "autonomous_cycle.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(log_level)  # Filtro configurable
            
            # Formato detallado con timestamp
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            # Handler para consola (stderr) - para Railway logs
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)  # Filtro configurable
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str, prefix: str = "DEBUG"):
        """Log mensaje de debug con prefijo personalizado"""
        self.logger.debug(f"[{prefix}] {message}")
    
    def info(self, message: str, prefix: str = "INFO"):
        """Log mensaje informativo con prefijo personalizado"""
        self.logger.info(f"[{prefix}] {message}")
    
    def error(self, message: str, prefix: str = "ERROR"):
        """Log mensaje de error con prefijo personalizado"""
        self.logger.error(f"[{prefix}] {message}")
    
    def warning(self, message: str, prefix: str = "WARNING"):
        """Log mensaje de advertencia con prefijo personalizado"""
        self.logger.warning(f"[{prefix}] {message}")
    
    def admin(self, message: str):
        """Log de eventos del admin panel"""
        self.info(message, prefix="ADMIN")
    
    def category(self, message: str):
        """Log de categorización de eventos"""
        self.info(message, prefix="CATEGORY")
    
    def bet(self, message: str):
        """Log de apuestas realizadas"""
        self.info(message, prefix="BET")
    
    def skip(self, message: str):
        """Log de apuestas saltadas"""
        self.info(message, prefix="SKIP")
    
    def cache(self, message: str):
        """Log de operaciones de caché (DEBUG level)"""
        self.debug(message, prefix="CACHE")
    
    def bankroll(self, message: str):
        """Log de gestión de bankroll"""
        self.info(message, prefix="BANKROLL MODE")
    
    def analysis(self, firm_name: str, message: str):
        """Log de análisis de una IA específica"""
        self.info(f"{firm_name} - {message}", prefix="INFO")
    
    def sanitize_text(self, text: str, max_length: int = 80) -> str:
        """
        Sanitiza y trunca texto para logging seguro.
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima (default: 80)
            
        Returns:
            Texto sanitizado y truncado
        """
        if not text:
            return ""
        sanitized = text[:max_length]
        if len(text) > max_length:
            sanitized += "..."
        return sanitized
    
    def log_bet_execution(self, firm_name: str, event_id: str, bet_size: float, 
                         event_snippet: str, success: bool, error_msg: str = None):
        """
        Log estructurado de ejecución de apuesta.
        
        Args:
            firm_name: Nombre de la IA
            event_id: ID del evento
            bet_size: Tamaño de la apuesta
            event_snippet: Descripción corta del evento (max 50 chars)
            success: True si la apuesta fue exitosa
            error_msg: Mensaje de error (si falló)
        """
        event_snippet_safe = self.sanitize_text(event_snippet, 50)
        
        if success:
            self.bet(f"{firm_name} - ${bet_size:.2f} on {event_snippet_safe} (event_id={event_id})")
        else:
            error_safe = self.sanitize_text(error_msg, 100) if error_msg else "Unknown error"
            self.error(f"{firm_name} - Failed bet on {event_snippet_safe} (event_id={event_id}): {error_safe}", prefix="BET ERROR")
    
    def log_risk_block(self, firm_name: str, risk_reason: str):
        """Log de bloqueo por riesgo"""
        reason_safe = self.sanitize_text(risk_reason, 150)
        self.info(f"{firm_name} - {reason_safe}", prefix="RISK BLOCK")
    
    def log_event_analysis(self, firm_name: str, event_description: str, 
                          prediction: dict, decision: dict, action: str):
        """
        Log detallado del análisis de cada evento (tanto BETs como SKIPs).
        
        Args:
            firm_name: Nombre de la IA
            event_description: Descripción del evento
            prediction: Diccionario con la predicción del LLM
            decision: Diccionario con la decisión final
            action: 'BET' o 'SKIP'
        """
        event_snippet = self.sanitize_text(event_description, 50)
        
        # Extraer scores de las 5 áreas
        sentiment_score = prediction.get('sentiment_score', 'N/A')
        news_score = prediction.get('news_score', 'N/A')
        technical_score = prediction.get('technical_score', 'N/A')
        fundamental_score = prediction.get('fundamental_score', 'N/A')
        volatility_score = prediction.get('volatility_score', 'N/A')
        
        probability = decision.get('probability', prediction.get('probabilidad_final_prediccion', 0))
        confidence = decision.get('confidence', prediction.get('nivel_confianza', 0))
        reason = self.sanitize_text(decision.get('reason', 'No reason provided'), 80)
        
        # Log estructurado
        if action == 'BET':
            bet_size = decision.get('bet_size', 0)
            self.bet(f"{firm_name} - ${bet_size:.2f} on '{event_snippet}' | Prob={probability:.2%}, Conf={confidence}% | Scores: S={sentiment_score}, N={news_score}, T={technical_score}, F={fundamental_score}, V={volatility_score}")
        else:  # SKIP
            self.skip(f"{firm_name} - '{event_snippet}' | Prob={probability:.2%}, Conf={confidence}% | Scores: S={sentiment_score}, N={news_score}, T={technical_score}, F={fundamental_score}, V={volatility_score} | Reason: {reason}")
    
    def get_recent_logs(self, lines: int = 500) -> str:
        """
        Obtiene las últimas N líneas del archivo de log.
        
        Args:
            lines: Número de líneas a retornar (default: 500)
            
        Returns:
            String con las últimas líneas del log
        """
        log_file = self.log_dir / "autonomous_cycle.log"
        
        if not log_file.exists():
            return "No logs available yet. Run a daily cycle to generate logs."
        
        try:
            # Leer las últimas N líneas con manejo robusto de encoding
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
        except Exception as e:
            return f"Error reading logs: {str(e)}"
    
    def get_log_file_path(self) -> str:
        """Retorna la ruta completa del archivo de log principal"""
        return str(self.log_dir / "autonomous_cycle.log")


# Instancia global del logger
autonomous_logger = AutonomousLogger()
