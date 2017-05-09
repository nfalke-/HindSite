'''
Navigator, the main driver of the $PROJECT_NAME project
uses selenium to run tests
'''
import time
import traceback
import os
import io
from selenium import webdriver
from utils import makedir, task
from camera import Video
from pyvirtualdisplay import Display
from PIL import Image, ImageChops, ImageDraw
import RunDao
import TestDao

BASE = './static'
BASELINE_DIR = 'baseline'
WIDTH = 1920
HEIGHT = 1080

BROWSERS = {
    'chrome': webdriver.Chrome,
    'firefox': webdriver.Firefox,
    'edge': webdriver.edge
}

class Navigator(object):
    def __init__(self, test_id, wait_time=5, browser=None):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        self.run_id = RunDao.add_run(test_id, now)
        self.directory = os.path.join(BASE, str(test_id), str(self.run_id))
        self.baseline = os.path.join(BASE, str(test_id), BASELINE_DIR)
        self.wait_time = wait_time
        self.task_list = TestDao.get_steps_for_test(test_id)
        self.test_passed = True
        self.test_screenshot_passed = True
        self.vdisplay = Display(backend='xvfb', size=(WIDTH, HEIGHT))
        self.vdisplay.start()
        if not browser or browser.lower() not in BROWSERS.keys():
            browser = webdriver.Firefox()
        else:
            browser = BROWSERS[browser.lower()]()

        self.last_clicked_on = None
        self.step_screenshot_passed = None
        self.step_passed = None
        self.screenshot_percent = None
        self.browser = browser
        self.browser.set_window_size(WIDTH, HEIGHT)
        self.browser.set_window_position(0, 0)
        self.commands = {
            'visit': self._visit,
            'click': self._click,
            'import': self._import,
            'insert': self._insert,
        }
        makedir(self.directory)
        makedir(self.baseline)
        self.video = Video(os.path.join(self.directory, "video"), 0, 0, WIDTH, HEIGHT)

    def _highlight(self, element):
        driver = element._parent
        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)
        original_style = element.get_attribute('style')
        for i in range(2):
            time.sleep(1)
            apply_style("background: yellow; border: 2px solid red;")
            time.sleep(1)
            apply_style(original_style)
        time.sleep(1)

    def _count_diff(self, image):
        black, total = 0, 0
        for pixel in image.getdata():
            if pixel == (0, 0, 0):
                black += 1
            total += 1
        difference = (float(total-black)/float(total))
        return difference

    def _diff_screenshots(self, a, b, opacity=0.85):
        point_table = ([0] + ([255] * 255))
        def new_gray(size, color):
            img = Image.new('L', size)
            dr = ImageDraw.Draw(img)
            dr.rectangle((0, 0) + size, color)
            return img
        size = (max(a.size[0], b.size[0]), max(a.size[1], b.size[1]))
        a, b = a.crop((0, 0)+size), b.crop((0, 0)+size)
        diff = ImageChops.difference(a, b).convert('L')
        thresholded_diff = diff
        for repeat in range(3):
            thresholded_diff = ImageChops.add(thresholded_diff, thresholded_diff)
        mask = new_gray(size, int(255 * (opacity)))
        shade = new_gray(size, 0)
        diff.point(point_table)
        c = diff.convert('RGB')
        c.paste(b, mask=diff)
        self.screenshot_percent = self._count_diff(c)
        new = a.copy()
        new.paste(shade, mask=mask)
        new.paste(b, mask=thresholded_diff)
        return new

    def _take_fullpage_screenshot(self):
        total_width = self.browser.execute_script("return document.body.offsetWidth")
        total_height = self.browser.execute_script("return document.body.parentNode.scrollHeight")
        partial_screenshot = self._take_partial_screenshot()
        client_width, client_height = partial_screenshot.size
        total_width = max(total_width, client_width)
        total_height = max(total_height, client_height)
        full_screenshot = Image.new('RGBA', (total_width, total_height))

        x, y = 0, 0
        while y < total_height:
            while x < total_width:
                self.browser.execute_script("window.scrollTo({0}, {1})".format(x, y))
                time.sleep(.2)
                partial_screenshot = self._take_partial_screenshot()
                full_screenshot.paste(partial_screenshot, (x, y))
                x += client_width
            x = 0
            y += client_height
        self.browser.execute_script("window.scrollTo({0}, {1})".format(0, 0))
        return full_screenshot

    def _take_partial_screenshot(self):
        return Image.open(io.BytesIO(self.browser.get_screenshot_as_png()))

    def _import(self, test_id):
        self.task_list = TestDao.get_steps_for_test(test_id) + self.task_list

    def _visit(self, url):
        self.browser.get(url)
        self.video.resume()
        time.sleep(2)
        self.video.pause()

    def _click(self, css_selector):
        element = self.browser.find_element_by_css_selector(css_selector)
        self.last_clicked_on = element
        self.video.resume()
        self._highlight(element)
        self.video.pause()
        element.click()
        time.sleep(2)
        self.video.resume()
        time.sleep(2)
        self.video.pause()

    def _insert(self, text):
        if self.last_clicked_on:
            self.last_clicked_on.send_keys(text)

    def _save_and_diff(self, screenshot_name):
        screenshot = self._take_fullpage_screenshot()
        screenshot.save(os.path.join(self.directory, '{}.png'.format(screenshot_name)))
        baseline_file = os.path.join(self.baseline, '{}.png'.format(screenshot_name))
        if os.path.isfile(baseline_file):
            baseline = Image.open(baseline_file)
            diff = self._diff_screenshots(screenshot, baseline)
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
            if True:
                self.test_passed = False
        time.sleep(self.wait_time)
        if task.take_screenshot:
            self._save_and_diff(task.screenshot_name)
            if self.screenshot_percent > task.threshold:
                self.step_screenshot_passed = False
                if True:
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
        while self.task_list:
            self._do_task(self.task_list.pop(0))
        self.video.resume()
        self.video.stop()
        self.browser.close()
        self.vdisplay.stop()
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        RunDao.update_run(self.run_id, now, self.test_passed, self.test_screenshot_passed)

# def main():
#     test_id = 101
#     task_list = (task('visit', 'https://reddit.com', True, 'home'),
#                  task('click', '#header-bottom-left > ul > li:nth-child(2) > a', True, 'new'))
#     n = Navigator(task_list, test_id, browser='chrome')
#     n.run()
