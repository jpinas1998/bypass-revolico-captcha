import os
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

audioToTextDelay = 10
filename = '1.mp3'
byPassUrl = 'https://www.revolico.com/insertar-anuncio.html'
googleIBMLink = 'https://speech-to-text-demo.ng.bluemix.net/'
option = webdriver.ChromeOptions()
option.add_argument('--disable-notifications')
option.add_argument("--mute-audio")
option.add_argument(
    "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) "
    "AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 "
    "Mobile/14E5239e Safari/602.1"
)


def delayTime():
    import random
    return random.randint(1, 5)


def audioToText(mp3Path):
    driver.execute_script('''window.open("","_blank");''')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(googleIBMLink)
    time.sleep(delayTime())

    # Upload file
    time.sleep(delayTime())
    root = driver.find_element_by_id('root').find_elements_by_class_name(
        'dropzone _container _container_large')
    btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    btn.send_keys(mp3Path)

    # Audio to text is processing
    time.sleep(delayTime())

    # Audio to text is processing
    time.sleep(audioToTextDelay)
    text = driver.find_element(
        By.XPATH,
        '//*[@id="root"]/div/div[7]/div/div/div'
    ).find_elements_by_tag_name('span')

    result = " ".join([each.text for each in text])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result


def saveFile(content, filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)


driver = webdriver.Chrome(ChromeDriverManager().install(),
                          options=option)
driver.get(byPassUrl)

time.sleep(delayTime())
googleClass = driver.find_elements_by_id('captcha')[0]

time.sleep(delayTime())
outeriframe = googleClass.find_element_by_tag_name('iframe')

time.sleep(delayTime())
outeriframe.click()

time.sleep(delayTime())
allIframesLen = driver.find_elements_by_tag_name('iframe')

time.sleep(delayTime())
audioBtnFound = False
audioBtnIndex = -1

for index in range(len(allIframesLen)):
    driver.switch_to.default_content()
    iframe = driver.find_elements_by_tag_name('iframe')[index]
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(delayTime())
    try:
        audioBtn = driver.find_element_by_id(
            'recaptcha-audio-button') or driver.find_element_by_id(
            'recaptcha-anchor')
        audioBtn.click()
        audioBtnFound = True
        audioBtnIndex = index
        break
    except Exception as e:
        pass

if audioBtnFound:
    try:
        while True:
            href = driver.find_element_by_id('audio-source').get_attribute(
                'src')
            response = requests.get(href, stream=True)
            saveFile(response, filename)

            response = audioToText(os.getcwd() + '/' + filename)
            print(response)

            driver.switch_to.default_content()
            iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]

            driver.switch_to.frame(iframe)
            inputbtn = driver.find_element_by_id('audio-response')
            inputbtn.send_keys(response)
            inputbtn.send_keys(Keys.ENTER)

            time.sleep(delayTime())
            errorMsg = driver.find_elements_by_class_name(
                'rc-audiochallenge-error-message')[0]

            if errorMsg.text == "" or errorMsg.value_of_css_property(
                    'display') == 'none':
                print("Success")
                break
    except Exception as e:
        print(e)
        print('Caught. Need to change proxy now')
else:
    print('Button not found. This should not happen.')
