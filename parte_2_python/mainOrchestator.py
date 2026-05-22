import pandas as pd
import logging
import os
from typing import Optional, Any
from datetime import datetime
from pathlib import Path

from DataQualityChecker import DataQualityChecker
from DataQualityReport import DataQualityReport
from DataNormalizer import DataNormalizer
from DataCleaning import DataCleaning

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

""""
    Clase de orquestador principal que se encargara de realizar:
        - Chequeo de calidad de los datos
        - Generar un reporte
        - Normalizar los datos
        - Eliminar repetidos
        - Guardar nuevo DataFrame en formato .xlsx
"""


class mainOrchestrator:
    def __init__(self, input_path: str = 'datos/base_vehiculos_livianos.xlsx', output_path: str = 'datos'):
        # Métricas del pipeline
        self.input_path = Path(input_path)
        self.output_dir = Path(output_path)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'rows_initial': None,
            'rows_final': None,
            'steps_completed' : []
        }
        self.output_path = None

    def _validate_input_file(self) -> bool:
        if not self.input_path.exists():
            logger.error(f"Archivo no encontrado: {self.input_path}")
            return False
        
        if not os.access(self.input_path, os.R_OK):
            logger.error(f"Archivo sin permisos de lectura: {self.input_path}")
            return False
        
        # Verificar que no está vacío
        if self.input_path.stat().st_size == 0:
            logger.error(f"Archivo vacío: {self.input_path}")
            return False
        
        return True
    
    def quality_check(self,df) -> Optional[dict]:
        try:
            logger.info("=== Paso 1: Verificando calidad de datos ===")
            dq = DataQualityChecker(df)
            data_report = dq.generate_report()
            
            return data_report
            
        except Exception as e:
            logger.exception(f"Error en quality_check: {e}")
            return None

    def generate_report(self, data_report: dict[str, Any]) -> Optional[str]:
        try:
            logger.info("=== Paso 2: Escribiendo reporte de calidad ===")
            dr = DataQualityReport()
            filename = dr.write_report(data_report)
            
            logger.info(f"Reporte de calidad guardado en: {filename}")
            
            return filename
            
        except Exception as e:
            logger.exception(f"Error en generate_report: {e}")
            return None

    def normalize(self,df : pd.DataFrame) -> Optional[pd.DataFrame] :
        try:
            logger.info("=== Paso 3: Normalizando información ===")
            dn = DataNormalizer(df)
            df_normalized = dn.normalizeData()
            
            logger.info(f"Normalización completada. Shape: {df_normalized.shape}")
            
            return df_normalized
            
        except Exception as e:
            logger.exception(f"Error en normalize: {e}")
            return None

    def clean(self, df : pd.DataFrame) -> Optional[pd.DataFrame]:
        try:
            logger.info("=== Paso 4: Limpiando datos ===")
            dc = DataCleaning(df)
            df_cleaned = dc.clean_data()
            
            logger.info(f"Limpieza completada. Shape: {df_cleaned.shape}")
            
            return df_cleaned
            
        except Exception as e:
            logger.exception(f"Error en clean: {e}")
            return None

    def save(self, df: pd.DataFrame, output_name: str = None) -> Optional[Path]:
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'vehiculos_procesados_{timestamp}.xlsx'
        
        output_path = self.output_dir / output_name
        
        try:
            logger.info(f"=== Paso 5: Guardando datos en {output_path} ===")
            df.to_excel(output_path, index=False)
            
            logger.info(f"Datos guardados exitosamente. Filas: {len(df)}, Columnas: {len(df.columns)}")
            
            return output_path
            
        except Exception as e:
            logger.exception(f"Error en step5_save: {e}")
            return None
    
    def _log_summary(self,output_path):
        logger.info("--------------------------")
        logger.info("RESUMEN DEL PIPELINE")
        logger.info("--------------------------")
        

        duration = None
        if self.metrics['start_time'] and self.metrics['end_time']:
            duration = self.metrics['end_time'] - self.metrics['start_time']
            logger.info(f"Tiempo total: {duration}")
        
        
        if output_path is not None:
            logger.info(f"Pasos completados: {len(self.metrics['steps_completed'])}/5")
            logger.info("Reporte de calidad generado")
            logger.info(f"Archivo final: {output_path}")

        logger.info("--------------------------")

    def run(self):
        try:
            # Validar archivo de entrada
            if not self._validate_input_file():
                raise FileNotFoundError(f"Archivo de entrada inválido: {self.input_path}")
            
            self.metrics['start_time'] = datetime.now()

            # Cargar datos
            logger.info(f"Cargando datos desde: {self.input_path}")
            df = pd.read_excel(self.input_path, sheet_name=0, header=2)
            self.metrics['rows_initial'] = len(df)
            logger.info(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
            
            # Paso 1: Verificacion de calidad
            quality_report = self.quality_check(df)
            if quality_report is None:
                raise Exception("Falló la verificación de calidad")

            self.metrics['steps_completed'].append('quality_check')
            
            # Paso 2: Generate reporte
            report_file = self.generate_report(quality_report)
            if report_file is None:
                logger.warning("No se pudo generar el reporte, continuando...")
            self.metrics['steps_completed'].append('generate_report')
            
            # Paso 3: Normalizacion 
            df_normalized = self.normalize(df)
            if df_normalized is None:
                raise Exception("Falló la normalización")
            self.metrics['steps_completed'].append('normalize')
            
            # Paso 4: Limpieza
            df_cleaned = self.clean(df_normalized)
            if df_cleaned is None:
                raise Exception("Falló la limpieza")
            self.metrics['rows_final'] = len(df_cleaned)
            self.metrics['steps_completed'].append('clean')
            
            # Paso 5: Guardado
            self.output_path = self.save(df_cleaned)
            if self.output_path is None:
                raise Exception("Falló el guardado")

            self.metrics['steps_completed'].append('save')
            
            logger.info("Pipeline completado exitosamente!")
            
        except Exception as e:
            logger.error(f"Pipeline falló: {e}")
        
        finally:
            self.metrics['end_time'] = datetime.now()
            self._log_summary(self.output_path)
        
    
if __name__ == '__main__':
    Orchestaror = mainOrchestrator()
    Orchestaror.run()
