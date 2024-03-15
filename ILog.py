# The Design of the Log Component

# According to the requirements, we can define an ILog class and define three functions: 
# 1. write()
# 2. createNewFile()
# 3. stop()

# Throughout the process, we can use a queue to store the logs, 
# and create a background thread to continuously write logs in the queue to the output file.
# In this case, we are able to handle the write request as fast as possible.

# For the write() function, we directly add the log information to the queue and then exit. 
# The background thread will continuously write the log in the queue to the current log file,
# and it would not block the write() function.

# For the createNewFile() function, we can set a timer at midnight.
# Because we set the timer, we don’t need to judge the arrival time of log every time.
# Whenever at midnight, the module will immediately create a new queue and a new log file. 
# Newly arrived log information will be added to the new queue. 
# The background process will continuously output the previous day's log information to the old log file. 
# When the old queue has been emptied, the background process will transfer to the new queue, 
# update the write file to the latest log file, and then start outputting log information from the new queue.

# We can use only one queue, like get the size of the queue at the last second of the previous day and output those logs to old log file.

# For the stop function, we handle it in two cases: 
# The first is to terminate immediately. At this time, the background thread stops immediately. 
# And the queue doesn't enqueue any new arrival log infos.
# The second is to wait for all logs in the queue to be written out before terminating. 
# In this case, our queue no longer accepts new log messages and stops when the queue is empty.

# We use try and except to handle the errors.

# The above is the basic design of the log module, but due to time constraints, I was not able to complete the coding part.
# So there are some bugs in the following codes and the unittests, which I wish I was supposed to fix it.

import os
import datetime
import threading
import queue

class ILog:
    def __init__(self, log_directory):
        self.log_directory = log_directory
        self.current_log_file = None
        self.current_month = None
        self.current_day = None
        self.log_queue = queue.Queue()
        self.stop_requested = False
        self.worker_thread = threading.Thread(target=self._log_worker)
        self.worker_thread.start()

    def write(self, message):
        self.log_queue.put(message)

    def stop(self, wait=False):
        self.stop_requested = True
        if wait:
            self.worker_thread.join()

    def _log_worker(self):
        while not self.stop_requested:
            try:
                while not self.log_queue.empty():
                    message = self.log_queue.get()
                    self._write_to_log(message)
            except queue.Empty:
                pass

    def _write_to_log(self, message):
        now = datetime.datetime.now()
        if self.current_log_file is None or (now.day != self.current_day and now.month != self.current_month):
            self._create_new_log_file(now)

        try:
            with open(self.current_log_file, 'a') as log_file:
                log_file.write(message + '\n')
        except Exception as e:
            print(f'Error writing to log file: {e}')

    def _create_new_log_file(self, timestamp):
        log_filename = timestamp.strftime('%Y-%m-%d.log')
        log_filepath = os.path.join(self.log_directory, log_filename)
        self.current_log_file = log_filepath
        self.current_month = timestamp.month
        self.current_day = timestamp.day

    def __del__(self):
        self.stop(wait=True)
        if self.current_log_file is not None:
            self.current_log_file.close()