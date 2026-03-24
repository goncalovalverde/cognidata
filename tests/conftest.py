"""
Pytest configuration and fixtures for CogniData tests
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "age": 65,
        "education_years": 12,
        "laterality": "diestro",
    }


@pytest.fixture
def sample_tmt_a_data():
    """Sample TMT-A test data"""
    return {
        "tiempo_segundos": 45.0,
        "errores": 0,
        "observaciones": "Prueba realizada sin dificultades",
    }


@pytest.fixture
def sample_tavec_data():
    """Sample TAVEC test data"""
    return {
        "ensayos": [8, 10, 12, 13, 14],
        "total_lista_a": 57,
        "lista_b": 6,
        "recuerdo_inmediato": 12,
        "recuerdo_diferido": 11,
        "reconocimiento": 15,
        "intrusiones": 0,
        "perseveraciones": 0,
        "falsos_positivos": 0,
    }


@pytest.fixture
def sample_fluidez_data():
    """Sample Fluidez FAS test data"""
    return {
        "letra_f": 14,
        "letra_a": 12,
        "letra_s": 13,
        "total": 39,
        "perseveraciones": 0,
        "intrusiones": 0,
    }


@pytest.fixture
def sample_rey_copia_data():
    """Sample Rey Figure Copy test data"""
    return {
        "puntuacion_bruta": 28.0,
        "tiempo_segundos": 180,
        "tipo_copia": "Tipo I - Constructivo",
        "observaciones": "Estrategia sistemática",
    }


@pytest.fixture
def sample_rey_memoria_data():
    """Sample Rey Figure Memory test data"""
    return {
        "puntuacion_bruta": 18.0,
        "tiempo_demora_minutos": 20,
        "observaciones": "Buenos detalles espaciales",
    }


@pytest.fixture
def expected_scores():
    """Expected normalized scores structure"""
    return {
        "puntuacion_escalar": int,
        "percentil": (int, float),
        "z_score": float,
        "clasificacion": str,
    }
