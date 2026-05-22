import os

"""
    Clase encargada que a partir de un diccionario de datos crea un reporte del DataFrame estudiado
    El reporte es generado como un archivo .txt
"""

class DataQualityReport:
    def __init__(self, report_file_path: str = "report.txt"):
        self.reportFile = open(report_file_path, "w")
        self.abs_path = os.path.abspath(report_file_path)

    def write_case(self, report: dict[str, any], varName: str):
        for column, missing_count in report[varName].items():
            missing_percentage = report['missing_percentage'][column]
            self.reportFile.write(f"\t{column} => Valores faltantes: {missing_count}, Porcentaje faltante: {missing_percentage}%\n")

    def write_report(self,dict_report: dict[str, any]) -> str:
        self.reportFile.write("Resultados de Completitud:\n")
        self.write_case(dict_report['completeness'], 'missing_counts')

        self.reportFile.write('\n----------------------------------\n')

        self.reportFile.write('\nResultados para unicidad \n')
        for key, value in dict_report['uniqueness'].items():
            self.reportFile.write(f"{key}:\n")
            self.reportFile.write(f"\tValores duplicados: {value['duplicate_counts']}, Porcentaje duplicado: {value['duplicate_percentage']}%\n")

        self.reportFile.write('\n----------------------------------\n')
        self.reportFile.write('\nResultados de datos que coinciden con rangos esperados\n')
        for key,value in dict_report['validity_result'].items():
            self.reportFile.write(f"{key}:\n")
            self.reportFile.write(f"\tValores invalidos {value}\n")
        
        self.reportFile.write('\n----------------------------------\n')
        self.reportFile.write('\nResultados de datos sea coherentes entre si\n')
        for key,value in dict_report['valid_correlation'].items():
            self.reportFile.write(f"{key}:\n")
            self.reportFile.write(f"\tValores invalidos: {value['invalid_counts']} Porcetanje: {value['invalid_percentage']}\n")

        self.reportFile.write('\n----------------------------------\n')
        self.reportFile.write('\nResultados de verificacion de tipo de datos sea correcto\n')
        for key,value in dict_report['valid_types'].items():
            self.reportFile.write(f"{key}:\n")
            self.reportFile.write(f"\tValores invalidos: {value['invalid_count']} Porcetanje: {value['invalid_percentage']}\n")
        

        return self.abs_path