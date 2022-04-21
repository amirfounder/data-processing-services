from typing import Any


def threaded_try_except(func):
    def wrapper(self, task: Any):
        try:

            summary = func(self, task) or {}
            summary['id'] = task.document_id

            with self.lock:
                self.report.log_success(summary)

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {task.document_id}')
            with self.lock:
                self.report.log_failure({
                    'id': task.document_id,
                    'reason': str(e)
                })

    return wrapper


def try_except(func):
    def wrapper(self, task: Any):
        try:

            summary = func(self, task) or {}
            summary['id'] = task.document_id

            self.report.log_success(summary)

        except Exception as e:
            print(f'Exception occurred : {str(e)}. Document ID : {task.document_id}')
            self.report.log_failure({
                'id': task.document_id,
                'reason': str(e)
            })

    return wrapper
