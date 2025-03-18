import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

def decorator_check(func):
    def wrapper(self, *args, **kwargs):
        if not self.__driver:
          print(f"\n 装饰器检测失败, {__name__} 没有__driver\n")
          return
        return func(self, *args, **kwargs)
    return wrapper


class WodDriver(object):
  __driver = None
  __instance = None
  def __new__(cls, *args, **kwargs):
    if not cls.__instance:
      cls.__instance = super(WodDriver, cls).__new__(cls)
    return cls.__instance

  @classmethod
  def get_instance(self):
    return self.__instance

  def login(self):
      if self.__driver == None:
        self.__driver = webdriver.Chrome()
      self.__driver.get('http://delta.world-of-dungeons.org')
      try:
          # 等待页面中的某个元素加载，这里假设是一个id为'content'的元素
          # 等待按钮可被点击
          if not self.wait('//*[@id="WodLoginBox"]/table/tbody/tr[4]/td[2]/input'):
              return True, f"看起来已经登录过了 或者页面超时"
          self.__driver.find_element(By.XPATH, '//*[@id="USERNAME"]').send_keys('')
          self.__driver.find_element(By.XPATH, '//*[@id="PASSWORT"]').send_keys('')
          self.__driver.find_element(By.XPATH, '//*[@id="WodLoginBox"]/table/tbody/tr[4]/td[2]/input').click()
          print("页面已加载完成！")
          print("登录按钮已点击")

          time.sleep(3)
          return True, "登录成功, 还睡了3秒"
      except Exception as e:
          print("登录wod 操作失败:", e)
          return False, e

  def __init__(self):
    if self.__driver == None:
      print(" *** init driver")
      chrome_options = Options()
      # chrome_options.add_argument("--headless")  # 无头模式
      chrome_options.add_argument("--ignore-certificate-errors")  # 忽略SSL错误
      chrome_options.add_argument("--allow-insecure-localhost")
      self.__driver = webdriver.Chrome(options=chrome_options)
      self.__driver.get('http://delta.world-of-dungeons.org')
      try:
        # 等待页面中的某个元素加载，这里假设是一个id为'content'的元素
        # 等待按钮可被点击
        submit_button = WebDriverWait(self.__driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="WodLoginBox"]/table/tbody/tr[4]/td[2]/input'))  # 根据需要修改XPath
        )
        self.__driver.find_element(By.XPATH, '//*[@id="USERNAME"]').send_keys('')
        self.__driver.find_element(By.XPATH, '//*[@id="PASSWORT"]').send_keys('')
        self.__driver.find_element(By.XPATH, '//*[@id="WodLoginBox"]/table/tbody/tr[4]/td[2]/input').click()
        print("*** 页面已加载完成！")
        print("*** 按钮已点击")
        target_element = WebDriverWait(self.__driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[2]/div/div/div/div/div/div[5]/a'))
        )
        target_element.click()
        time.sleep(1)
        #driver.find_element(By.XPATH, '//*[@id="menu_dungeon"]/a').click()
        
      except Exception as e:
        print("开启浏览器 登录wod 操作失败:", e)

  def __del__(self):
      if self.__driver:
          self.__driver.quit()
      super().__del__()

  def geturl(self):
    return self.__driver.current_url

  # @decorator_check
  def exce_js(self, code):
    try:
      return True, self.__driver.execute_script(code)
    except Exception as e:
      print(f"\n\n 执行js失败, 代码: {code}\n error: {e} \n")
      return False, None

  # @decorator_check
  def open_get_page(self, url):
    self.__driver.get(url)
    return self.__driver.page_source

  def get_page(self):
    return self.__driver.page_source

  # @decorator_check
  def open(self, url):
    try:
      self.__driver.get(url)
    except Exception as e:
      print(f"\n\n open 失败 {url} {e} \n\n")

  # @decorator_check
  def find_xpath(self, id):
    try:
      return self.__driver.find_element(By.XPATH, id)
    except:
      return None

  def finds_xpath(self, id):
    try:
      return self.__driver.find_elements(By.XPATH, id)
    except:
      return None 

  def find_name(self, name):
    try:
      return self.__driver.find_element(By.NAME, name)
    except:
      return None

  def wait(self, xpath_id):
    try:
      WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_id)))
      return True
    except Exception as e:
      print(f"\n\n wait 失败 {xpath_id} \n\n")
      return None

WodDriver()
