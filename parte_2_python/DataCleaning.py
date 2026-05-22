import yaml
import pandas as pd


"""
    Clase para realizar una limpieza de un DataFrame
    Se eliminaran los datos repetidos a partir de los criterios definidos previamente:
        - Codigo tecnico
        - Numero de certificado

"""

class DataCleaning:
    def __init__(self, df):
        self.df = df
        self.cm = load_yaml()


    def clean_data_by_uniq_values(self):
        # Aquí puedes agregar tus funciones de limpieza de datos
        self.df.drop_duplicates(subset=[self.cm['CODIGO_TECNICO']], keep ='first')
        self.df.drop_duplicates(subset=[self.cm['N_CERT']], keep ='first')

    def clean_data(self) -> pd.DataFrame:
        self.clean_data_by_uniq_values()

        return self.df


def load_yaml():
    """Carga el mapeo de columnas desde YAML"""
    with open('./parte_2_python/columnMapping.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)



""""
    Mejoras aplicadas a la limpieza de datos:
        1.- Limpieza de valores duplicados en codigo de informe tecnico
        2.- Limpieza de valores duplicados en numero de certificado

"""
