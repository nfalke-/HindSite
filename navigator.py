from selenium import webdriver
from time import sleep, time
from PIL import Image, ImageChops, ImageDraw
from io import StringIO, BytesIO

class Navigator(object):
    def __init__(self, task_list, wait_time=5, browser=None):
        if not browser:
            browser = webdriver.Firefox()
        self.browser = browser
        self.wait_time = wait_time
        self.task_list = task_list
        self.video_frames = []
        self.full_screenshots = []
        self.commands = {
            'visit': self._visit,
            'click': self._click,
        }

    def _new_gray(self, size, color):
        img = Image.new('L', size)
        dr = ImageDraw.Draw(img)
        dr.rectangle((0, 0) + size, color)
        return img

    point_table = ([0] + ([255] * 255))
    def _diff_screenshots(self, a, b, opacity=0.85):
        size = (max(a.size[0], b.size[0]), max(a.size[1], b.size[1]))
        a, b = a.crop((0, 0)+size), b.crop((0, 0)+size)
        diff = ImageChops.difference(a, b).convert('L')
        thresholded_diff = diff
        for repeat in range(3):
            thresholded_diff  = ImageChops.add(thresholded_diff, thresholded_diff)
        mask = self._new_gray(size, int(255 * (opacity)))
        shade = self._new_gray(size, 0)
        new = a.copy()
        new.paste(shade, mask=mask)
        new.paste(b, mask=thresholded_diff)
        return new


    def _take_fullpage_screenshot(self):
        total_width = self.browser.execute_script("return document.body.offsetWidth")
        total_height = self.browser.execute_script("return document.body.parentNode.scrollHeight")
        client_width = self.browser.execute_script("return document.body.clientWidth")
        client_height = self.browser.execute_script("return window.innerHeight")
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

    def _add_slide_to_video(self):
        #TODO: figure out how to make videos and replace this with that
        self.video_frames.append(self._take_partial_screenshot())

    def _visit(self, url):
        self.browser.get(url)
        self._add_slide_to_video()

    def _click(self, css_selector):
        element = self.browser.find_element_by_css_selector(css_selector)
        self._highlight(element)
        element.click()

    def _do_task(self, task):
        self.commands[task[0]](task[1])
        sleep(self.wait_time)
        self._add_slide_to_video()
        self.full_screenshots.append(self._take_fullpage_screenshot())

    def _highlight(self, element):
        """Highlights (blinks) a Selenium Webdriver element"""
        driver = element._parent
        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                  element, s)
        original_style = element.get_attribute('style')
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        self._add_slide_to_video()
        apply_style("background: yellow; border: 2px solid red;")
        self._add_slide_to_video()
        apply_style(original_style)
        self._add_slide_to_video()

    def run(self):
        for task in self.task_list:
            self._do_task(task)
        #TODO: correct file storage instead of this crap
        for i, frame in enumerate(self.video_frames):
            frame.save('frame{}.png'.format(i))
        for i, screenshot in enumerate(self.full_screenshots):
            #b = Image.open('full_screenshot{}.png'.format(i))
            #self._diff_screenshots(screenshot, b).save('diff{}.png'.format(i))
            screenshot.save('full_screenshot{}.png'.format(i))

