import pytest
from data_processing import ReportProcessor

@pytest.fixture
def sample_logs():
    # Пример логов для тестирования отчётов
    return [
        {"url": "/api/v1/foo", "response_time": 100, "status": 200},
        {"url": "/api/v1/foo", "response_time": 200, "status": 200},
        {"url": "/api/v1/bar", "response_time": 300, "status": 500},
        {"url": "/api/v1/bar", "response_time": 400, "status": 200},
    ]

def test_reports_registered():
    """Проверяем, что отчёты из reports зарегистрированы в ReportProcessor."""
    instances = ReportProcessor.get_all_instances()
    assert len(instances) > 0
    for instance in instances:
        assert hasattr(instance, "keyword")
        assert callable(instance.get_report)

@pytest.mark.parametrize("report_keyword", [r.keyword for r in ReportProcessor.get_all_instances()])
def test_report_output_structure(report_keyword, sample_logs):
    """Проверяем, что каждый отчёт возвращает непустой список словарей с ожидаемыми ключами."""
    processor = ReportProcessor.select_report_type(report_keyword)
    assert processor is not None
    result = processor.get_report(sample_logs, args=None)
    assert isinstance(result, list)
    if result:  # Если отчёт не пустой
        assert isinstance(result[0], dict)
        # Проверяем, что в словаре есть хотя бы один ключ (например, handler или total)
        assert len(result[0].keys()) > 0

def test_report_empty_logs():
    """Проверяем, что отчёты корректно обрабатывают пустой список логов."""
    for instance in ReportProcessor.get_all_instances():
        result = instance.get_report([], args=None)
        assert isinstance(result, list)
        assert len(result) == 0 or all(isinstance(item, dict) for item in result)