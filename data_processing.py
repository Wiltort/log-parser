from typing import Callable


class ReportProcessor:
    _instances = []  # все экземпляры

    def __init__(self, keyword: str, get_report: Callable):

        self.keyword = keyword
        self.get_report = get_report
        self._instances.append(self)

    @classmethod
    def get_all_instances(cls):
        return cls._instances

    @classmethod
    def select_report_type(cls, input_str: str):
        for report in cls.get_all_instances():
            if input_str == report.keyword:
                return report
        else:
            return None

    @classmethod
    def report(cls, *, keyword: str):
        def decorator(func: Callable):
            instance = cls(keyword=keyword, get_report=func)
            func.report_instance = instance
            return func
        return decorator
