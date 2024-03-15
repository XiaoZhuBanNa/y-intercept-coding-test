# The Design of the Unit Tests:

# 1. Test Case: Writing a Log Message
#    Input: Log message "Test log message"
#    Expected Output: The log message is enqueued and written to the log file correctly.

# 2. Test Case: Writing Multiple Log Messages
#    Input: Log messages "Message 1", "Message 2", "Message 3"
#    Expected Output: All the log messages are enqueued and written to the log file in the correct order.

# 3. Test Case: Cross Midnight
#    Input: Wait until midnight and write a log message
#    Expected Output: A new log file is created with a new timestamp, and the log message is written to the new file.

# 4. Test Case: Stop Immediately
#    Input: Call the stop() method immediately after writing a log message
#    Expected Output: The log component stops immediately without waiting for the outstanding logs to be written. No further logs are processed.

# 5. Test Case: Stop and Wait
#    Input: Write multiple log messages and then call the stop(wait=True) method
#    Expected Output: The log component stops after processing all the outstanding logs. All the logs are written to the log file correctly.

# 6. Test Case: Error Handling
#    Input: Simulate an error while writing a log message (e.g., permission denied, disk full)
#    Expected Output: The log component handles the error, prints an error message, 
#    and continues processing the remaining log messages without crashing the calling application.

import datetime
import time
import os
import unittest
from unittest.mock import patch
from test import ILog

class ILogTests(unittest.TestCase):
    def setUp(self):
        self.log_directory = './logs'
        self.log = ILog(self.log_directory)

    def tearDown(self):
        self.log.stop(wait=True)
        log_files = os.listdir(self.log_directory)
        for file in log_files:
            file_path = os.path.join(self.log_directory, file)
            os.remove(file_path)

    def test_write_logs(self):
        message = 'Test log message'
        self.log.write(message)
        time.sleep(1)
        log_files = os.listdir(self.log_directory)
        self.assertEqual(len(log_files), 1)
        log_file_path = os.path.join(self.log_directory, log_files[0])
        with open(log_file_path, 'r') as log_file:
            content = log_file.read()
        self.assertIn(message, content)

    def test_new_files_created_at_midnight(self):
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2024, 3, 15, 23, 59, 59)
            self.log.write('Log message 1')
            time.sleep(1)
            log_files = os.listdir(self.log_directory)
            self.assertEqual(len(log_files), 1)
            mock_datetime.now.return_value = datetime.datetime(2024, 3, 16, 0, 0, 1)
            self.log.write('Log message 2')
            time.sleep(1)
            log_files = os.listdir(self.log_directory)
            self.assertEqual(len(log_files), 2)

    def test_stop_behavior(self):
        self.log.write('Log message 1')
        self.log.stop()
        self.log.write('Log message 2')
        time.sleep(1)
        log_files = os.listdir(self.log_directory)
        self.assertEqual(len(log_files), 1)
        log_file_path = os.path.join(self.log_directory, log_files[0])
        with open(log_file_path, 'r') as log_file:
            content = log_file.read()
        self.assertIn('Log message 1', content)
        self.assertNotIn('Log message 2', content)


if __name__ == '__main__':
    unittest.main()
    