import time
from Daos import SuiteDao
from Daos import TestDao

while True:
    for scheduled_id, suite_id, test_id in TestDao.get_tests_scheduled_later_than_now():
        print("posting to /suites/{}/tests/{}/run".format(suite_id, test_id))
        print("updating {}".format(scheduled_id))
        TestDao.schedule_next_test(scheduled_id)
    for scheduled_id, suite_id in SuiteDao.get_suites_scheduled_later_than_now():
        print("posting to /suites/{}/run".format(suite_id))
        print("updating {}".format(scheduled_id))
        SuiteDao.schedule_next_suite(scheduled_id)
    time.sleep(60)


