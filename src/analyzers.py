from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union


class ContentAnalyzer(ABC):
    """ Базовый класс анализатора контента"""

    @abstractmethod
    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """
        Анализ данных
        
        Args:
            data: Данные для анализа
            threshold: Порог срабатывания
            
        Returns:
            Кортеж (is_violation, score, reason)
        """
        pass


class NudityAnalyzer(ContentAnalyzer):
    """Анализатор контента наготы"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ наготы"""
        if "nudity" not in data:
            return False, 0.0, None

        nudity_data: Dict = data["nudity"]
        score = probabilities_sum(nudity_data)

        is_violation = score > threshold
        reason = "Nudity detected" if is_violation else None

        return is_violation, score, reason


class ViolenceAnalyzer(ContentAnalyzer):
    """Анализатор контента насилия"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ насилия"""
        if "violence" not in data:
            return False, 0.0, None

        violence_data = data["violence"]
        score = violence_data.get("prob", 0.0)

        is_violation = score > threshold
        reason = "Violence detected" if is_violation else None

        return is_violation, score, reason


class WeaponAnalyzer(ContentAnalyzer):
    """Анализатор контента оружия"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ оружия"""
        if "weapon" not in data:
            return False, 0.0, None

        weapon_data: Dict = data["weapon"]
        score = probabilities_sum(weapon_data)

        is_violation = score > threshold
        reason = "Weapon detected" if is_violation else None

        return is_violation, score, reason


class AlcoholAnalyzer(ContentAnalyzer):
    """Анализатор контента алкоголя"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ алкоголя"""
        if "alcohol" not in data:
            return False, 0.0, None

        alcohol_data = data["alcohol"]
        score = alcohol_data.get("prob", 0.0)

        is_violation = score > threshold
        reason = "Alcohol detected" if is_violation else None

        return is_violation, score, reason


class GoreAnalyzer(ContentAnalyzer):
    """Анализатор контента крови"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ крови"""
        if "gore" not in data:
            return False, 0.0, None

        gore_data = data["gore"]
        score = gore_data.get("prob", 0.0)

        is_violation = score > threshold
        reason = "Gore detected" if is_violation else None

        return is_violation, score, reason


class DrugAnalyzer(ContentAnalyzer):
    """Анализатор контента наркотиков"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ наркотиков"""
        if "recreational_drug" not in data:
            return False, 0.0, None

        drug_data = data["recreational_drug"]
        score = drug_data.get("prob", 0.0)

        is_violation = score > threshold
        reason = "Drug detected" if is_violation else None

        return is_violation, score, reason


class OffensiveAnalyzer(ContentAnalyzer):
    """Анализатор контента агрессия"""

    def analyze(self, data: Dict[str, Any], threshold: float) -> Tuple[bool, float, Optional[str]]:
        """Анализ агрессии"""
        if "offensive" not in data:
            return False, 0.0, None

        offensive_data: Dict = data["offensive"]
        score = probabilities_sum(offensive_data)

        is_violation = score > threshold
        reason = "Offensive detected" if is_violation else None

        return is_violation, score, reason


class ContentAnalyzerFactory:
    """Фабрика анализаторов контента"""

    @staticmethod
    def create_analyzers(models: str) -> List[ContentAnalyzer]:
        """
        Создание анализаторов на основе моделей
        
        Args:
            models: Строка с моделями через запятую
            
        Returns:
            Список анализаторов
        """
        analyzers = []
        model_list = [model.strip() for model in models.split(",")]

        analyzer_map = {
            "nudity-2.0": NudityAnalyzer(),
            "nudity": NudityAnalyzer(),
            "violence": ViolenceAnalyzer(),
            "weapon": WeaponAnalyzer(),
            "alcohol": AlcoholAnalyzer(),
            "gore": GoreAnalyzer(),
            "drug": DrugAnalyzer(),
            "offensive": OffensiveAnalyzer()
        }

        for model in model_list:
            if model in analyzer_map:
                analyzers.append(analyzer_map[model])

        return analyzers

def probabilities_sum(data: Union[Dict]) -> float:
    """Подсчёт всех вероятностей"""
    total = 0.0
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "none":  # Пропускаем все ключи "none"
                continue
            if isinstance(value, float):
                total += value
            elif isinstance(value, dict):
                total += probabilities_sum(value)
    return total
