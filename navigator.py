from selenium import webdriver
from time import sleep, time
from PIL import Image, ImageChops, ImageDraw
from io import StringIO, BytesIO
import os
from camera import Video
from pyvirtualdisplay import Display

base = './static'
WIDTH=3935
HEIGHT=1080

class Navigator(object):
    def __init__(self, task_list, test_id, wait_time=5, browser=None):
        self.vdisplay = Display(backend='xvfb', size=(WIDTH, HEIGHT))
        self.vdisplay.start()
        if not browser:
            browser = webdriver.Chrome()
        self.runtime = str(int(time() * 1000))
        self.directory = os.path.join(base, str(test_id), self.runtime)
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        self.browser = browser
        self.browser.maximize_window()
        #self.browser.set_window_size(WIDTH, HEIGHT)
        #self.browser.set_window_position(0, 0)
        self.wait_time = wait_time
        self.task_list = task_list
        self.full_screenshots = []
        self.commands = {
            'visit': self._visit,
            'click': self._click,
        }
        self.video = Video(os.path.join(self.directory, "video"), 0, 0, WIDTH, HEIGHT)
        self.image_no = 0


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
            thresholded_diff  = ImageChops.add(thresholded_diff, thresholded_diff)
        mask = new_gray(size, int(255 * (opacity)))
        shade = new_gray(size, 0)
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
                #print("window.scrollTo({0}, {1})".format(x, y))
                partial_screenshot = self._take_partial_screenshot()
                full_screenshot.paste(partial_screenshot, (x, y))
                x += client_width
            x = 0
            y += client_height
        self.browser.execute_script("window.scrollTo({0}, {1})".format(0, 0))
        #topnav = self.browser.find_element_by_tag_name("header")
        #self.browser.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", topnav)
        return full_screenshot

    def _take_partial_screenshot(self):
        return Image.open(BytesIO(self.browser.get_screenshot_as_png()))

    def _visit(self, url):
        self.browser.get(url)
        self.video.resume()
        sleep(2)
        self.video.pause()

    def _click(self, css_selector):
        element = self.browser.find_element_by_css_selector(css_selector)
        self.video.resume()
        self._highlight(element)
        self.video.pause()
        element.click()
        self.video.resume()
        sleep(2)
        self.video.pause()

    def _do_task(self, task):
        self.image_no += 1
        filename = os.path.join(self.directory, "{}.png".format(self.image_no))
        self.browser.save_screenshot(filename)
        sleep(2)
        self.commands[task[0]](task[1])
        sleep(self.wait_time)
        self.full_screenshots.append(self._take_fullpage_screenshot())

    def _highlight(self, element):
        """Highlights (blinks) a Selenium Webdriver element"""
        driver = element._parent
        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                  element, s)
        original_style = element.get_attribute('style')
        sleep(.5)
        apply_style("background: yellow; border: 2px solid red;")
        sleep(1)
        apply_style(original_style)
        sleep(.5)

    def run(self):
        start = time()
        for task in self.task_list:
            self._do_task(task)
        self.video.resume()
        self.video.stop()
        self.browser.close()
        for i, screenshot in enumerate(self.full_screenshots):
            #b = Image.open('full_screenshot{}.png'.format(i))
            #self._diff_screenshots(screenshot, b).save('diff{}.png'.format(i))
            screenshot.save(os.path.join(self.directory, 'full_screenshot{}.png'.format(i)))
        self.vdisplay.stop()
        return self.runtime

if __name__ == "__main__":
    test_id = 100
    task_list = (('visit', 'https://docs.python.org/3/library/io.html'),
                ('click', 'body > div.document > div.sphinxsidebar > div.sphinxsidebarwrapper > p:nth-child(6) > a'))
    n = Navigator(task_list, test_id)
    n.run()

