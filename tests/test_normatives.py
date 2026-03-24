"""
Unit tests for the NormativeCalculator service
"""

import pytest
from services.normatives import NormativeCalculator, calculator


class TestNormativeCalculator:
    """Tests for NormativeCalculator class"""

    def test_classify_superior(self):
        """Test classification for superior performance (percentil >= 75)"""
        result = calculator._classify(80)
        assert result == "Superior"

    def test_classify_normal(self):
        """Test classification for normal performance (25 <= percentil < 75)"""
        result = calculator._classify(50)
        assert result == "Normal"

    def test_classify_limitrofe(self):
        """Test classification for borderline performance (10 <= percentil < 25)"""
        result = calculator._classify(15)
        assert result == "Limítrofe"

    def test_classify_deficitario(self):
        """Test classification for deficient performance (percentil < 10)"""
        result = calculator._classify(5)
        assert result == "Deficitario"

    def test_classify_boundary_75(self):
        """Test classification at boundary (percentil = 75)"""
        result = calculator._classify(75)
        assert result == "Superior"

    def test_classify_boundary_25(self):
        """Test classification at boundary (percentil = 25)"""
        result = calculator._classify(25)
        assert result == "Normal"

    def test_classify_boundary_10(self):
        """Test classification at boundary (percentil = 10)"""
        result = calculator._classify(10)
        assert result == "Limítrofe"

    def test_percentile_to_z_mean(self):
        """Test z-score calculation at mean (percentil = 50)"""
        z = calculator._percentile_to_z(50)
        assert abs(z) < 0.01

    def test_percentile_to_z_high(self):
        """Test z-score calculation for high percentile"""
        z = calculator._percentile_to_z(97.5)
        assert 1.9 < z < 2.1

    def test_percentile_to_z_low(self):
        """Test z-score calculation for low percentile"""
        z = calculator._percentile_to_z(2.5)
        assert -2.1 < z < -1.9

    def test_percentile_to_z_zero(self):
        """Test z-score calculation at zero percentile (capped)"""
        z = calculator._percentile_to_z(0)
        assert z == -3.0

    def test_percentile_to_z_100(self):
        """Test z-score calculation at 100 percentile (capped)"""
        z = calculator._percentile_to_z(100)
        assert z == 3.0

    def test_calculate_tmt_a(self):
        """Test TMT-A calculation"""
        result = calculator.calculate(
            test_type="TMT-A", raw_score=45.0, age=65, education_years=12
        )

        assert "puntuacion_escalar" in result
        assert "percentil" in result
        assert "z_score" in result
        assert "clasificacion" in result
        assert isinstance(result["puntuacion_escalar"], int)
        assert 1 <= result["puntuacion_escalar"] <= 19

    def test_calculate_tavec(self):
        """Test TAVEC calculation"""
        result = calculator.calculate(
            test_type="TAVEC", raw_score=57, age=65, education_years=12
        )

        assert "puntuacion_escalar" in result
        assert "percentil" in result
        assert "clasificacion" in result

    def test_calculate_fluidez_fas(self):
        """Test Fluidez FAS calculation"""
        result = calculator.calculate(
            test_type="Fluidez-FAS", raw_score=39, age=65, education_years=12
        )

        assert "puntuacion_escalar" in result
        assert "percentil" in result
        assert "clasificacion" in result

    def test_calculate_without_table(self):
        """Test calculation for test type without normative table"""
        result = calculator.calculate(
            test_type="TMT-B", raw_score=120.0, age=65, education_years=12
        )

        assert "puntuacion_escalar" in result
        assert "percentil" in result
        assert "clasificacion" in result
        assert "norma_aplicada" in result

    def test_calculate_tmt_a_with_normative(self, tmp_path):
        """Test TMT-A calculation with actual normative table"""
        result = calculator.calculate(
            test_type="TMT-A", raw_score=30.0, age=50, education_years=10
        )

        assert result["clasificacion"] in [
            "Superior",
            "Normal",
            "Limítrofe",
            "Deficitario",
        ]


class TestNormativeCalculatorInterpolation:
    """Tests for score interpolation functionality"""

    def test_interpolate_scores_exact_match(self):
        """Test interpolation when exact score exists"""
        conversion_table = {
            "40": {"pe": 10, "percentil": 50},
            "50": {"pe": 12, "percentil": 65},
        }

        pe, percentil = calculator._interpolate_scores(40, conversion_table)
        assert pe == 10
        assert percentil == 50

    def test_interpolate_scores_between(self):
        """Test interpolation between two scores"""
        conversion_table = {
            "40": {"pe": 10, "percentil": 50},
            "50": {"pe": 12, "percentil": 65},
        }

        pe, percentil = calculator._interpolate_scores(45, conversion_table)
        assert 10 <= pe <= 12
        assert 50 <= percentil <= 65

    def test_interpolate_scores_below_min(self):
        """Test interpolation below minimum score"""
        conversion_table = {
            "40": {"pe": 10, "percentil": 50},
            "50": {"pe": 12, "percentil": 65},
        }

        pe, percentil = calculator._interpolate_scores(30, conversion_table)
        assert pe == 10
        assert percentil == 50

    def test_interpolate_scores_above_max(self):
        """Test interpolation above maximum score"""
        conversion_table = {
            "40": {"pe": 10, "percentil": 50},
            "50": {"pe": 12, "percentil": 65},
        }

        pe, percentil = calculator._interpolate_scores(60, conversion_table)
        assert pe == 12
        assert percentil == 65


class TestNormativeCalculatorEdgeCases:
    """Tests for edge cases in normative calculations"""

    def test_calculate_with_extreme_age(self):
        """Test calculation with very young/old patient age"""
        result_young = calculator.calculate(
            test_type="TMT-A", raw_score=30.0, age=18, education_years=10
        )

        result_old = calculator.calculate(
            test_type="TMT-A", raw_score=30.0, age=90, education_years=10
        )

        assert result_young["clasificacion"] is not None
        assert result_old["clasificacion"] is not None

    def test_calculate_with_extreme_education(self):
        """Test calculation with extreme education years"""
        result_low = calculator.calculate(
            test_type="TMT-A", raw_score=60.0, age=50, education_years=0
        )

        result_high = calculator.calculate(
            test_type="TMT-A", raw_score=30.0, age=50, education_years=25
        )

        assert result_low["clasificacion"] is not None
        assert result_high["clasificacion"] is not None
