"""
Servicio mejorado de cálculo de normas neuropsicológicas con tablas NEURONORMA reales
"""
import numpy as np
from scipy import stats
from typing import Dict, Optional
import json
import os


class NormativeCalculator:
    """Calculador de puntuaciones normativas según tablas NEURONORMA"""
    
    def __init__(self):
        self.normative_tables = {}
        self._load_normative_tables()
    
    def _load_normative_tables(self):
        """Cargar todas las tablas normativas desde archivos JSON"""
        tables_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'normative_tables')
        
        # Mapeo de tipos de test a archivos
        test_files = {
            'TMT-A': 'tmt_a.json',
            'TAVEC': 'tavec.json',
            'Fluidez-FAS': 'fluidez_fas.json'
        }
        
        for test_type, filename in test_files.items():
            filepath = os.path.join(tables_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.normative_tables[test_type] = json.load(f)
    
    def calculate(
        self,
        test_type: str,
        raw_score: float,
        age: int,
        education_years: int
    ) -> Dict:
        """
        Calcular puntuación escalar, percentil y clasificación usando tablas NEURONORMA
        
        Args:
            test_type: Tipo de test ('TMT-A', 'TMT-B', 'TAVEC', etc.)
            raw_score: Puntuación bruta
            age: Edad del paciente
            education_years: Años de escolaridad
        
        Returns:
            Dict con pe, percentil, z_score, clasificacion
        """
        
        # Si tenemos tabla NEURONORMA para este test, usarla
        if test_type in self.normative_tables:
            return self._calculate_from_table(test_type, raw_score, age, education_years)
        
        # Fallback a cálculo simulado para tests sin tabla aún
        return self._calculate_simulated(test_type, raw_score, age, education_years)
    
    def _calculate_from_table(
        self,
        test_type: str,
        raw_score: float,
        age: int,
        education_years: int
    ) -> Dict:
        """Calcular usando tablas NEURONORMA reales"""
        
        table = self.normative_tables[test_type]
        
        # Encontrar rango de edad apropiado
        age_range = None
        for ar in table['age_ranges']:
            if ar['age_min'] <= age <= ar['age_max']:
                age_range = ar
                break
        
        if not age_range:
            # Si no hay rango, usar el más cercano
            age_range = table['age_ranges'][0]
        
        # Encontrar rango de educación apropiado
        education_range = None
        for er in age_range['education_ranges']:
            if er['education_min'] <= education_years <= er['education_max']:
                education_range = er
                break
        
        if not education_range:
            # Si no hay rango, usar el más cercano
            education_range = age_range['education_ranges'][0]
        
        # Obtener tabla de conversión
        conversion_table = education_range['conversion_table']
        
        # Buscar puntuación bruta exacta o interpolar
        raw_score_str = str(int(raw_score))
        
        if raw_score_str in conversion_table:
            # Coincidencia exacta
            pe = conversion_table[raw_score_str]['pe']
            percentil = conversion_table[raw_score_str]['percentil']
        else:
            # Interpolar entre valores más cercanos
            pe, percentil = self._interpolate_scores(raw_score, conversion_table)
        
        # Calcular z-score desde percentil
        z_score = self._percentile_to_z(percentil)
        
        # Clasificación clínica
        clasificacion = self._classify(percentil)
        
        return {
            "puntuacion_escalar": pe,
            "percentil": percentil,
            "z_score": round(z_score, 2),
            "clasificacion": clasificacion,
            "norma_aplicada": {
                "fuente": table['source'],
                "test": table['test_name'],
                "rango_edad": f"{age_range['age_min']}-{age_range['age_max']}",
                "rango_educacion": f"{education_range['education_min']}-{education_range['education_max']}"
            }
        }
    
    def _interpolate_scores(self, raw_score: float, conversion_table: dict) -> tuple:
        """Interpolación lineal entre puntuaciones brutas"""
        
        # Obtener todas las puntuaciones brutas disponibles
        available_scores = sorted([int(k) for k in conversion_table.keys()])
        
        # Encontrar límites para interpolación
        lower_scores = [s for s in available_scores if s <= raw_score]
        upper_scores = [s for s in available_scores if s >= raw_score]
        
        if not lower_scores:
            # Menor que el mínimo
            lowest = str(available_scores[0])
            return conversion_table[lowest]['pe'], conversion_table[lowest]['percentil']
        
        if not upper_scores:
            # Mayor que el máximo
            highest = str(available_scores[-1])
            return conversion_table[highest]['pe'], conversion_table[highest]['percentil']
        
        lower = lower_scores[-1]
        upper = upper_scores[0]
        
        if lower == upper:
            # Coincidencia exacta
            key = str(lower)
            return conversion_table[key]['pe'], conversion_table[key]['percentil']
        
        # Interpolación lineal
        lower_key = str(lower)
        upper_key = str(upper)
        
        ratio = (raw_score - lower) / (upper - lower)
        
        pe_lower = conversion_table[lower_key]['pe']
        pe_upper = conversion_table[upper_key]['pe']
        pe = pe_lower + ratio * (pe_upper - pe_lower)
        
        percentil_lower = conversion_table[lower_key]['percentil']
        percentil_upper = conversion_table[upper_key]['percentil']
        percentil = percentil_lower + ratio * (percentil_upper - percentil_lower)
        
        return round(pe), round(percentil, 1)
    
    def _percentile_to_z(self, percentil: float) -> float:
        """Convertir percentil a z-score"""
        if percentil <= 0:
            return -3.0
        if percentil >= 100:
            return 3.0
        return stats.norm.ppf(percentil / 100)
    
    def _calculate_simulated(
        self,
        test_type: str,
        raw_score: float,
        age: int,
        education_years: int
    ) -> Dict:
        """Cálculo simulado para tests sin tabla NEURONORMA aún"""
        
        # Usar distribución normal para simular
        mean = 50
        std = 10
        
        z_score = (raw_score - mean) / std
        percentil = stats.norm.cdf(z_score) * 100
        pe = int(10 + (z_score * 3))
        pe = max(1, min(19, pe))
        
        clasificacion = self._classify(percentil)
        
        return {
            "puntuacion_escalar": pe,
            "percentil": round(percentil, 1),
            "z_score": round(z_score, 2),
            "clasificacion": clasificacion,
            "norma_aplicada": {
                "fuente": "Simulado (NEURONORMA pendiente)",
                "test": test_type,
                "rango_edad": f"{age-5}-{age+5}",
                "rango_educacion": f"{education_years-2}-{education_years+2}"
            }
        }
    
    def _classify(self, percentil: float) -> str:
        """Clasificación clínica según percentil"""
        if percentil >= 75:
            return "Superior"
        elif percentil >= 25:
            return "Normal"
        elif percentil >= 10:
            return "Limítrofe"
        else:
            return "Deficitario"


calculator = NormativeCalculator()
