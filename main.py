import argparse
import json
from tabulate import tabulate
from data_processing import ReportProcessor
from reports import * # чтобы все отчеты подгрузились


def parse_args():
    parser = argparse.ArgumentParser(description='Process log files')
    parser.add_argument('--file', nargs='+', required=True, help='path to log file(s)')
    parser.add_argument(
        '--report',
        required=True,
        choices=[r.keyword for r in ReportProcessor.get_all_instances()],
        help='Type of report'
    )
    parser.add_argument('--date', required=False, help='date in format `2025-22-06`')
    return parser.parse_args()


def read_logs(file_paths):
    logs = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs


def main():
    args = parse_args()
    logs = read_logs(args.file)
    processor = ReportProcessor.select_report_type(args.report)
    if args.date:
        try:
            year, day, month = args.date.split('-')
        except ValueError:
            print('Incorrect data format (YYYY-DD-MM)')

    report = processor.get_report(logs=logs, date=f'{year}-{month}-{day}')
    if not report:
        print("Empty report data")
        return

    headers = report[0].keys()
    table = [[item[key] for key in headers] for item in report]
    print(tabulate(table, headers=headers, tablefmt='grid'))


if __name__ == '__main__':
    main()
