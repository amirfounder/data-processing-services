from math import inf
from typing import Dict


class Report:
    def __init__(self):
        self.status = '--'
        self.succeeded_count = 0
        self.failed_count = 0
        self.summaries = []

    def reset(self):
        self.status = '--'
        self.succeeded_count = 0
        self.failed_count = 0
        self.summaries = []

    def log_success(self, summary: Dict):
        self.succeeded_count += 1
        print(f'Success {self.succeeded_count}')
        summary['status'] = 'SUCCESS'
        self.summaries.append(summary)

    def log_failure(self, summary: Dict):
        self.failed_count += 1
        print(f'Failed {self.failed_count}')
        summary['status'] = 'FAILED'
        self.summaries.append(summary)

    def finalize(self):
        self.status = 'COMPLETE'
        self.summaries.sort(key=lambda s: s.get('id', inf))
        return self.as_dict()

    def as_dict(self):
        return {
            'status': self.status,
            'succeeded_count': self.succeeded_count,
            'failed_count': self.failed_count,
            'summaries': self.summaries
        }
