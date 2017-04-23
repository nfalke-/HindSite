from navigator import Navigator
import database_access


task_list = (('visit', 'http://www.reddit.com'), )
if __name__ == '__main__':
#    task_list = database_access.get_steps_for_test(1)
    n = Navigator(task_list)
    n.run()
