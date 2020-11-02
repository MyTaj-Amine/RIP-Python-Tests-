import unittest
from selenium import webdriver
import threading
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TwoUsersTesting(unittest.TestCase):

    def setUp(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--incognito')
        self.options.add_argument('--start-maximized')
        self.drivers = []

    def open_browser(self, i):
        print("new browser")
        print(self)
        print(i)
        try:
            driver = webdriver.Chrome(executable_path=r"C:\Users\34603\PycharmProjects\Rip_Python_Test\Drivers\chromedriver.exe", options=self.options)
            if i == 1:
                driver.set_page_load_timeout(10)
            elif i== 2:
                driver.set_page_load_timeout(15)
            else:
                driver.set_page_load_timeout(20)
            driver.get('http://localhost:8080/RIP/SSE?expId=PeriodicSendOnDelta')
        except Exception:
            print('time out')
            events = driver.find_element_by_xpath("/html[1]/body[1]/pre[1]")
            if i == 1:
                try:
                    driver.set_page_load_timeout(20)
                    driver.refresh()
                except Exception:
                    events = driver.find_element_by_xpath("/html[1]/body[1]/pre[1]")
            elif i == 2:
                try:
                    driver.set_page_load_timeout(15)
                    driver.refresh()
                except Exception:
                    events = driver.find_element_by_xpath("/html[1]/body[1]/pre[1]")
            else:
                try:
                    driver.set_page_load_timeout(10)
                    driver.refresh()
                except Exception:
                    events = driver.find_element_by_xpath("/html[1]/body[1]/pre[1]")
        # Do something validate results...
        # Store the result
        self.results[i] = events.is_displayed()

    def test_ServerAccess_Immediately(self):
        # How many browsers/clients
        N = 3
        # Each thread must modify only its own results (stored at position i)
        self.results = [False for i in range(0, N)]
        threads = []
        for i in range(0, N):
            t = threading.Thread(target=self.open_browser, args=[i])
            threads.append(t)
            time.sleep(0.5)
            threads[i].start()
        # Wait for threads to end
        for i in range(0, N):
            threads[i].join()
            self.assertTrue(self.results[i])
        # Do any other global check

if __name__ == "__main__":
    unittest.main()
