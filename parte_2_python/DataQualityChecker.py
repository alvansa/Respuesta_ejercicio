import datetime
from typing import Optional
import pandas as pd
import yaml

"""
    Clase para evaluar la calidad de un dataFrame a partir de evaluacion de completitud
    unicidad, validez de los tipos de datos y que esten dentro de un rango esperado.
    Para este caso se asumieron 2 causas de unicidad que son:
        - Codigo Tecnico 
        - Numero de certificado
    La clase devuelve un diccionario que se puede exportar en el formato deseado.
"""

class DataQualityChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.results = {}
        self.cm = load_yaml()

    def check_completeness(self) -> dict[str, any]:
        missing_counts = self.df.isnull().sum()
        total_rows = len(self.df)
        missing_percentage = (missing_counts/total_rows) * 100
        return {
            'missing_counts' : missing_counts.to_dict(),
            'missing_percentage' : missing_percentage.round(2).to_dict()
        }
    
    def check_uniqueness(self, subset: Optional[list]) -> dict[str, any]:
        if subset is None:
            subset = self.df.columns.tolist()

        total_rows = len(self.df)
        duplicate_flag = self.df.duplicated(subset=subset, keep=False)
        
        duplicate_counts = duplicate_flag.sum()
        duplicate_percentage = (duplicate_counts/total_rows) * 100


        return {
            'duplicate_counts' : duplicate_counts,
            'duplicate_percentage' : round(duplicate_percentage, 2)
        }
    
    def check_validity(self, validation_rules: dict[str, any]) -> dict[str, any]:
        # Ejemplo de reglas de validación:
        # validation_rules = {
        # Fecha de Homologación: {
        #     'range': ('2000-01-01', '2026-1-1') 
        # }
        #
        #    Transmisión : {
        #       'regex': {'[M|A]'}
        # }

        if validation_rules is None:
            return {}
        invalid_counts = {}
        for col, rules in validation_rules.items():
            invalid_inidices = set()
            if col not in self.df.columns:
                continue
                
            if 'regex' in rules:
                pattern = rules['regex']
                invalid_regex = ~self.df[col].astype(str).str.match(pattern)
                invalid_inidices.update(self.df[invalid_regex].index)

            if 'range_datetime' in rules:
                min_val, max_val = rules['range_datetime']
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                invalid_range = self.df[col].between(min_val, max_val, inclusive= 'both')
                invalid_inidices.update(self.df[~invalid_range].index)
            

            if 'range_number' in rules:
                min_val, max_val = rules['range_number']
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                invalid_range = self.df[col].between(min_val, max_val, inclusive= 'both')
                invalid_inidices.update(self.df[~invalid_range].index)

            invalid_counts[col] = len(invalid_inidices)


        return invalid_counts
    
    def check_correlation(self , validation_rules: dict[str, any]) -> dict[str, any]:
        # Funcion para comprobar la correlacion entre dos columnas
        # Si una columna es "Combustion" => Cilindrada > 0

        # Ejemplo de validation_rules
        # Propulsión :{
        #       'value' : 'Combustión' 
        #       'column_values': {
        #            'Cilindrada': lambda x: x > 0,    
        #   }
        # }

        if validation_rules is None:
            return {}
        invalid_counts = 0
        total_rows = len(self.df)
        for col, rules in validation_rules.items():
            invalid_inidices = set()
            if col not in self.df.columns:
                continue
            if 'value' in rules:
                expected_value = rules['value']
                base_value = self.df[col] == expected_value
                
                if 'column_values' in rules:
                    for related_col, condition in rules['column_values'].items():
                        if related_col in self.df.columns:
                            self.df[related_col] = pd.to_numeric(self.df[related_col], errors='coerce')
                            condition_met = self.df[related_col].apply(condition)
                            invalid_value = base_value & ~condition_met
                            invalid_inidices.update(self.df[invalid_value].index)

            invalid_counts = len(invalid_inidices)
            invalid_percentage = (invalid_counts/total_rows) * 100

            invalid_counts = {
                'invalid_counts' : len(invalid_inidices),
                'invalid_percentage' : round(invalid_percentage, 2)
            }

        return invalid_counts

    
    def check_type(self, column: str, expected_type: type) -> dict[str, any]:
        # Ejemplo de tipos esperados
        #   - Float 
        #   - datetime
        #   - str

        if column not in self.df.columns:
            return {'error': f'Columna {column} no encontrada en el DataFrame.'}
        
        invalid_count = self.df[~self.df[column].apply(lambda x: isinstance(x, expected_type))].shape[0]
        total_rows = len(self.df)
        invalid_percentage = (invalid_count / total_rows) * 100
        return {
            'invalid_count': invalid_count,
            'invalid_percentage': round(invalid_percentage, 2)
        }

    
    def generate_report(self) -> dict[str, any]:
        dict_report = {}

        #Chequeo de completitud
        completeness_results = self.check_completeness()
        dict_report['completeness'] = completeness_results

        #Chequeo de unicidad
        uniqueness_results_Codigo_Informe = self.check_uniqueness(subset=[self.cm['CODIGO_TECNICO']])
        uniqueness_results_Numero_Certificado = self.check_uniqueness(subset=[self.cm['N_CERT']])

        dict_report['uniqueness'] = {
            'Codigo_Informe_Tecnico': uniqueness_results_Codigo_Informe,
            'Numero_Certificado': uniqueness_results_Numero_Certificado
        }

        #Chequeo de validacion de rango de los datos
        validity_results = self.check_validity(validation_rules={
            self.cm['FECHA_HOMOLOGACION']: {
                'range_datetime': ('2000-01-01', '2026-5-19') 
            },
            self.cm['TRANSMISION']: {
                'regex': '^[M|A]$'
            },
            self.cm['RENDIMIENTO_COMBUSTIBLE']:{
                'range_number' : (1, float('inf')) 
            },
            self.cm['PBV'] : {
                'range_number' : (1, float('inf'))
            }
        })

        dict_report['validity_result'] = validity_results

        valid_correlation_prop_cil = self.check_correlation(validation_rules={
            self.cm['PROPULSION']:{
                'value' : 'Combustión',
                'column_values': {
                    self.cm['CILINDRADA']: lambda x: x > 0,
                }
            },
        })

        valid_correlation_prop_em = self.check_correlation(validation_rules={
            self.cm['PROPULSION']:{
                'value' : 'Combustión',
                'column_values': {
                    self.cm['EMISIONES_CO2'] : lambda x: x > 0, 
                }
            },
        })
        valid_correlation_prop_rend = self.check_correlation(validation_rules={
            self.cm['PROPULSION']:{
                'value' : 'Combustión',
                'column_values': {
                    self.cm['RENDIMIENTO_COMBUSTIBLE'] : lambda x: x > 0, 
                }
            },
        })
        valid_correlation_prop_norm = self.check_correlation(validation_rules={
            self.cm['PROPULSION']:{
                'value' : 'Combustión',
                'column_values': {
                    self.cm['NORMA_EUROPEA'] : lambda x: x > 0, 
                }
            },
        })


        dict_report['valid_correlation'] = {
            'Propulsion/Cilindrada': valid_correlation_prop_cil,
            'Propulsion/Emisiones': valid_correlation_prop_em,
            'Propulsion/Rendimiento': valid_correlation_prop_rend,
            'Propulsion/Norma': valid_correlation_prop_norm,
        }

        #Chequeo de tipo de los datos
        validTypesDates = self.check_type(self.cm['FECHA_HOMOLOGACION'], datetime.datetime)
        validTypesRendimiento = self.check_type(self.cm['RENDIMIENTO_COMBUSTIBLE'], float)
        validTypePBV = self.check_type(self.cm['PBV'], float)

        dict_report['valid_types'] = {
            'Fecha Homologacion': validTypesDates,
            'Rendimiento combustible' : validTypesRendimiento,
            'P.B.V': validTypePBV,
        }

        return dict_report
    

def load_yaml():
    # Carga el mapeo de columnas desde YAML
    with open('parte_2_python/columnMapping.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    dt = pd.read_excel('datos/base_vehiculos_livianos.xlsx', sheet_name=0, header=2)
    dq_checker = DataQualityChecker(dt)
    dict = dq_checker.generate_report()
    for key,value in dict.items():
        print(key,value)


if __name__ == "__main__":
    main()