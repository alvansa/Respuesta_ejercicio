import pandas as pd
from unidecode import unidecode
import yaml

"""
    Clase para realizar aplicar reglas de normalizacion estandar a un DataFrame
        - Eliminacion de espacios multiples
        - Eliminacion de tildes
        - Pasar a minuscula
        - Entre otros
"""

class DataNormalizer:
    def __init__(self, df):
        self.df = df
        self.cm = load_yaml()

    def normalize_column_names(self):
        self.df.columns = [col.strip() for col in self.df.columns]
    
    def standardize_transminission_values(self):
        self.df[self.cm['TRANSMISION']] = self.df[self.cm['TRANSMISION']].str.upper().str.strip().apply(unidecode)
        self.df[self.cm['TRANSMISION']] = self.df[self.cm['TRANSMISION']].replace({'MANUAL': 'M', 'AUTOMATICA': 'A'})

    def standarize_nullValues(self, columns: list):
        for col in columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def standarize_text(self,column):
        self.df[column] = self.df[column].apply(self.standarizeText)

    def standarizeText(self,value):
        if pd.isna(value):
            return value
        return unidecode(str(value).lower().strip())
    
    
    def normalizeData(self) -> pd.DataFrame:
        self.normalize_column_names()
        self.standardize_transminission_values()
        self.standarize_nullValues([self.cm['EMISIONES_CO2'], self.cm['NORMA_EUROPEA'], self.cm['RENDIMIENTO_COMBUSTIBLE']])
        self.standarize_text(self.cm['COMBUSTIBLE'])
        self.standarize_text(self.cm['PROPULSION'])

        return self.df

    

def load_yaml():
    """Carga el mapeo de columnas desde YAML"""
    with open('./parte_2_python/columnMapping.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    df = pd.read_excel('./datos/base_vehiculos_livianos.xlsx', sheet_name=0, header=2)
    normalizer = DataNormalizer(df)
    normalizer.normalizeData()

if __name__ == "__main__":
    main()



"""
Mejorar aplicadas
    1.- Estadarizacion de valores nullos a tipo nulo para mejor manejo
    2.- Normalizacion de columna de transmicion
    3.- Normalizacion de valores de texto para eliminar espacios extra, tildes y convertir a minuscula
"""


