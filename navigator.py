'''
Navigator, the main driver of the $PROJECT_NAME project
uses selenium to run tests
'''
import time
import traceback
import os
import io
import utils
from camera import Video
from PIL import Image, ImageChops, ImageDraw
from Daos import TestDao, RunDao
from config import config
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def run_test(test_id: int, size: tuple, browser: str):
    '''run a test'''
    navigator = Navigator(test_id, (size), browser=browser)
    navigator.run()


os.environ['PATH'] += ':'+os.path.join(os.getcwd(), config.PATH_TO_DRIVERS)

BROWSERS = {
    'chrome': webdriver.Chrome,
    'firefox': webdriver.Firefox,
    'edge': webdriver.edge,
    'opera': webdriver.Opera
}


class Navigator(object):
    '''
    This object is essentially a wrapper around webdriver that records and takes screenshots
    '''
    def __init__(self, test_id, size, wait_time=5, browser=None):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        self.run_id = RunDao.add_run(test_id, now)
        self.wait_time = wait_time
        self.task_list = TestDao.get_steps_for_test(test_id)
        self.test_passed = True
        self.test_screenshot_passed = True
        if not browser or browser.lower() not in BROWSERS.keys():
            self.browser = webdriver.Firefox()
        else:
            self.browser = BROWSERS[browser.lower()]()

        self.last_clicked_on = None
        self.step_screenshot_passed = None
        self.step_passed = None
        self.screenshot_percent = None

        self.browser.set_window_position(0, 0)
        self.browser.set_window_size(*size)
        self.browser.maximize_window()
        self.commands = {
            'visit': self._visit,
            'click': self._click,
            'import': self._import,
            'input': self._insert,
            'sleep': self._sleep,
            'refresh': self._refresh,
            'execute': self._execute,
            'assert': self._assert,
        }
        self.directory = os.path.join(config.BASE, str(test_id), str(self.run_id))
        self.baseline = os.path.join(config.BASE, str(test_id), config.BASELINE_DIR)

        utils.makedir(self.directory)
        utils.makedir(self.baseline)
        self.video = Video(os.path.join(self.directory, "video"), 0, 0, *size)

    def _highlight(self, style, element):
        driver = element._parent

        def apply_style(style):
            '''
                applies a style to an element
            '''
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                  element, style)
        original_style = element.get_attribute('style')
        for _ in range(2):
            time.sleep(.5)
            apply_style(style)
            time.sleep(.5)
            apply_style(original_style)

    def _count_diff(self, image):
        black, total = 0, 0
        for pixel in image.getdata():
            if pixel == (0, 0, 0):
                black += 1
            total += 1
        difference = (float(total-black)/float(total))
        return difference

    def _diff_screenshots(self, image_a, image_b, opacity=0.85):
        point_table = ([0] + ([255] * 255))

        def new_gray(size, color):
            '''
            returns a darkened mask to highlight differences
            '''
            img = Image.new('L', size)
            darkened = ImageDraw.Draw(img)
            darkened.rectangle((0, 0) + size, color)
            return img
        size = (max(image_a.size[0], image_b.size[0]), max(image_a.size[1], image_b.size[1]))
        image_a, image_b = image_a.crop((0, 0)+size), image_b.crop((0, 0)+size)
        diff = ImageChops.difference(image_a, image_b).convert('L')
        thresholded_diff = diff
        for _ in range(3):
            thresholded_diff = ImageChops.add(thresholded_diff, thresholded_diff)
        mask = new_gray(size, int(255 * (opacity)))
        shade = new_gray(size, 0)
        diff.point(point_table)
        image_c = diff.convert('RGB')
        image_c.paste(image_b, mask=diff)
        self.screenshot_percent = self._count_diff(image_c)
        new = image_a.copy()
        new.paste(shade, mask=mask)
        new.paste(image_b, mask=thresholded_diff)
        return new

    def _take_fullpage_screenshot(self):
        total_width = self.browser.execute_script(
            "return (document.width !== undefined) ? document.width : document.body.offsetWidth")
        total_height = self.browser.execute_script(
            """return Math.max(document.body.scrollHeight, document.body.offsetHeight,
                               document.documentElement.clientHeight, document.documentElement.scrollHeight,
                               document.documentElement.offsetHeight );""")
	
        partial_screenshot = self._take_partial_screenshot()
        client_width, client_height = partial_screenshot.size
        total_width = max(total_width, client_width)
        total_height = max(total_height, client_height)
        full_screenshot = Image.new('RGBA', (total_width, total_height))
        full_screenshot.paste(partial_screenshot, (0, 0))
        self.browser.execute_script("a = document.getElementsByTagName('header')[0]; a ? a.setAttribute('style', 'position: absolute; top: 0px;') : null;")

        x, y = 0, 0
        while y < total_height:
            print(y)
            y += client_height
            y_offset = y
            if y + client_height > total_height:
                y_offset = total_height - client_height
            while x < total_width:
                self.browser.execute_script("window.scrollTo({0}, {1})".format(x, y))
                time.sleep(.2)
                partial_screenshot = self._take_partial_screenshot()
                full_screenshot.paste(partial_screenshot, (x, y_offset))
                x += client_width
            x = 0
        self.browser.execute_script("window.scrollTo({0}, {1})".format(0, 0))
        return full_screenshot

    def _take_partial_screenshot(self):
        return Image.open(io.BytesIO(self.browser.get_screenshot_as_png()))

    def _import(self, test_id):
        self.task_list = list(TestDao.get_steps_for_test(test_id)) + self.task_list

    def _refresh(self, _):
        self.video.resume()
        time.sleep(.5)
        self.browser.refresh()
        time.sleep(.5)
        self.video.pause()

    def _visit(self, url):
        self.browser.get(url)
        self.video.resume()
        time.sleep(2)
        self.video.pause()

    def _execute(self, script):
        self.video.resume()
        try:
            self.browser.execute_script(script)
        except WebDriverException:
            pass
        time.sleep(2)
        self.video.pause()

    def _click(self, css_selector):
        element = self.browser.find_element_by_css_selector(css_selector)
        self.last_clicked_on = element
        self.video.resume()
        self._highlight("background: yellow; border: 2px solid red;", element)
        self.video.pause()
        element.click()
        time.sleep(1)
        self.video.resume()
        time.sleep(1)
        self.video.pause()

    def _assert(self, css_selector):
        element = self.browser.find_element_by_css_selector(css_selector)
        self.last_clicked_on = element
        self.video.resume()
        self._highlight("background: green; border: 2px solid green;", element)
        self.video.pause()
        time.sleep(1)
        self.video.resume()
        time.sleep(1)
        self.video.pause()

    def _insert(self, text):
        if self.last_clicked_on:
            self.last_clicked_on.send_keys(text)

    def _sleep(self, time_in_seconds):
        time.sleep(float(time_in_seconds))

    def _save_and_diff(self, screenshot_name):
        screenshot = self._take_fullpage_screenshot()
        screenshot.save(os.path.join(self.directory, '{}.png'.format(screenshot_name)))
        baseline_file = os.path.join(self.baseline, '{}.png'.format(screenshot_name))
        if os.path.isfile(baseline_file):
            baseline_image = Image.open(baseline_file)
            diff = self._diff_screenshots(screenshot, baseline_image)
            diff.save(os.path.join(self.directory, 'diff_{}.png'.format(screenshot_name)))

    def _do_task(self, task):
        if not self.test_passed:
            return
        time.sleep(2)
        self.step_passed = True
        self.step_screenshot_passed = True
        self.screenshot_percent = -1.0
        try:
            self.commands[task.action](task.args)
        except:
            traceback.print_exc()
            self.step_passed = False
            if not task.is_optional:
                self.test_passed = False
        time.sleep(self.wait_time)
        if task.take_screenshot:
            self._save_and_diff(task.screenshot_name)
            if self.screenshot_percent > task.threshold:
                self.step_screenshot_passed = False
                if task.is_optional:
                    self.test_screenshot_passed = False

        RunDao.add_run_step(
            self.run_id,
            task.action,
            task.args,
            self.step_passed,
            task.take_screenshot,
            self.screenshot_percent,
            self.step_screenshot_passed,
            (task.screenshot_name or '')
        )

    def run(self):
        '''
        runs the test
        '''
        self.task_list = list(self.task_list)
        while self.task_list:
            self._do_task(self.task_list.pop(0))
        self.video.resume()
        self.video.stop()
        self.browser.quit()
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        RunDao.update_run(self.run_id, now, self.test_passed, self.test_screenshot_passed)

# def main():
#     test_id = 101
#     task_list = (task('visit', 'https://reddit.com', True, 'home', 1),
#                  task('click', '#header-bottom-left > ul > li:nth-child(2) > a', True, 'new', 1))
#     n = Navigator(task_list, test_id, browser='')
#     n.run()
