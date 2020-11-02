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
                driver.set_page_load_timeout(20)
            else:
                driver.set_page_load_timeout(30)
            driver.get('http://localhost:8080/RIP/SSE?expId=PeriodicSendOnDelta')
        except Exception:
            print('time out')
            events = driver.find_element_by_xpath("/html[1]/body[1]/pre[1]")
        # Do something validate results...
        # ...
        # Store the result
        self.data[i] = events.text
        print(self.data[i])
        self.results[i] = events.is_displayed()

    def test_ServerAccess_differentConnectTime(self):
        # How many browsers/clients
        N = 2
        # Each thread must modify only its own results (stored at position i)
        self.data = ["" for i in range(0, N)]
        self.results = [False for i in range(0, N)]
        threads = []
        for i in range(0, N):
            t = threading.Thread(target=self.open_browser, args=[i])
            threads.append(t)
            time.sleep(10)
            threads[i].start()
        # Wait for threads to end
        for i in range(0, N):
            threads[i].join()
            # check that the users receive events
            self.assertTrue(self.results[i])
        # if the users dont connected in the same time then check that the second users data are in the first user data
        self.assertIn(self.data[1], self.data[0])
        # Do any other global check

if __name__ == "__main__":
    unittest.main()
