from collections import defaultdict
from data_processing import ReportProcessor


@ReportProcessor.report(keyword='average')
def generate_average_report(logs, args):
    """
    Generate a report with the average response time per endpoint.

    Args:
        logs (list): List of log entries (dicts).

    Returns:
        list: List of dicts with keys 'handler', 'total', and 'avg_response_time'.
    """
    date = None
    if args and args.date:
        try:
            year, day, month = args.date.split('-')
            date = f'{year}-{month}-{day}'
        except ValueError:
            print('Incorrect data format (YYYY-DD-MM)')
    endpoint_data = defaultdict(lambda: {'count': 0, 'total_time': 0})
    for log in logs:
        endpoint = log.get('url')
        response_time = log.get('response_time')
        if endpoint and response_time is not None:
            if date is not None:
                log_date = log['@timestamp']
                if date not in log_date:
                    continue
            endpoint_data[endpoint]['count'] += 1
            endpoint_data[endpoint]['total_time'] += response_time

    report = []
    for endpoint, data in endpoint_data.items():
        avg_time = data['total_time'] / data['count'] if data['count'] > 0 else 0
        report.append({
            'handler': endpoint,
            'total': data['count'],
            'avg_response_time': round(avg_time, 3)
        })

    return sorted(report, key=lambda x: -x['total'])
