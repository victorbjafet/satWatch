import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


import pandas as pd




#logs to file and optionally prints to stdout
def write(*writeStr):
    with open("log.txt", "at") as logFile:
        logFile.write(str(writeStr[0]) + "\n")
    if len(writeStr) > 1: #more than 1 parameter, prints to jupyter output as well
        print(writeStr[0].strip())



#since i do the same while loop for every element during the auto login process, i decided to make it a function to prevent repetitive code
def attemptInteract(timeout: int, errorText: str, strategy: By, locator: str, keyInput: bool, keyText: str):
    #timeout: time, in seconds, to timeout the function if the element is not located and interacted with
    #errortext: the text that is output to the log file and as the exception message if the timeout is reached
    #strategy: selenium "By" object, indicating what stategy to use to locate the element on the page
    #locator: a string providing the value that should be used with the strategy to locate the target element
    #keyInput: true if the element requires some form of keyboard/text input, such as a text field. will click the element otherwise
    #keyText: the text to enter if keyInput is true. should be None if keyInput is false.
    startTime = time.time()
    terminateCondition = False
    while not terminateCondition:
        try:
            # print("finding element: " + str(strategy) + ": " + locator) #debug
            interactElement = driver.find_element(strategy, locator)
            if keyInput:
                interactElement.clear()
                interactElement.send_keys(keyText)
            else:
                interactElement.click()
            terminateCondition = True
        except:
            pass
        if time.time() - startTime >= timeout and not terminateCondition:
            write(errorText + " (raising error)", True)
            raise Exception(errorText)








#put your email and password in the variables below to have it saved (optional)
# email = ""
# password = ""

email = ""
password = ""

if not email:
    email = input("Enter your collegeboard login email: ")
if not password:
    password = input("Enter your collegeboard login password: ")

refreshBuffer = 15 #how long (in seconds) the program will wait before refreshing the page after checking for a new score to prevent rate limiting. in testing, 5 seconds has gotten rate limited, while 20 seconds hasn't






write("\n\n" + time.strftime("%m/%d/%Y") + "@" + time.strftime("%H:%M:%S", time.localtime()) + " | New Session", True)

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging']) #prevents annoying terminal outputs
# options.add_argument("--headless") #uncomment if you dont want a browser window opening (may possibly be faster but im not sure)


driver = webdriver.Chrome(options=options)
driver.get("https://mysat.collegeboard.org/dashboard")


checkCounter = 0 #just counting the amount of checks (checks happen on first boot, on login, or on page refreshes)
done = False #will only become true if 

while not done:
    checkCounter += 1
    write(time.strftime("%m/%d/%Y") + "@" + time.strftime("%H:%M:%S", time.localtime()) + " | Check #" + str(checkCounter))

    loggedIn = False
    statusFound = False
    firstStatusCheck = True
    startTime = time.time()
    #this while loop will find out if the webpage is logged in or not
    #if it can't find the elements that indicate either of these things within 20 seconds, it will time out and throw an error
    while not statusFound:
        try:
            loginButton = driver.find_element(By.ID, "qc-id-login-button-continue")
            loggedIn = False
            statusFound = True
            write("\t" + time.strftime("%m/%d/%Y") + "@" + time.strftime("%H:%M:%S", time.localtime()) + " | Not logged in")
        except:
            pass

        try:
            listElement = driver.find_element(By.CLASS_NAME, "qc-assessment-summary-card-list")
            loggedIn = True
            statusFound = True
            write("\t" + time.strftime("%m/%d/%Y") + "@" + time.strftime("%H:%M:%S", time.localtime()) + " | Logged in")        
        except:
            pass

        if firstStatusCheck and not statusFound:
            write("\tInitial status check failed, page likely loading (20 second timeout started)")
            firstStatusCheck = False

        if time.time() - startTime >= 20 and not statusFound:
            write("\tPage not loading after 20 seconds, internet disconnected or rate limited or something else went wrong (raising error)")
            raise Exception("Page not loading after 20 seconds, internet disconnected or rate limited or something else went wrong")


    if not loggedIn:
        write("\tNot logged in, attempting auto login")

        write("\tFinding login button")
        attemptInteract(20, "Sign in button not found after 20 seconds, internet disconnected or rate limited or something else went wrong" , By.ID, "qc-id-login-button-continue", False, None)

        write("\tEntering email")
        attemptInteract(20, "Email not entered after 20 seconds, internet disconnected or rate limited or something else went wrong", By.ID, "idp-discovery-username", True, email)

        write("\tSubmitting email")
        attemptInteract(20, "Email button not found after 20 seconds, internet disconnected or rate limited or something else went wrong" , By.ID, "idp-discovery-submit", False, None)

        write("\tEntering password")
        attemptInteract(20, "Password not entered after 20 seconds, internet disconnected or rate limited or something else went wrong" , By.ID, "okta-signin-password", True, password)
        
        time.sleep(0.5) #if you hit submit immediately after entering the password, nothing happens so give it a buffer
        write("\tSubmitting credentials")
        attemptInteract(20, "Password not entered after 20 seconds, internet disconnected or rate limited or something else went wrong" , By.ID, "okta-signin-submit", False, None)

        time.sleep(1) #give it some time to process the credentials before rerunning the check loop

        write("\t" + time.strftime("%m/%d/%Y") + "@" + time.strftime("%H:%M:%S", time.localtime()) + " | Credentials Entered", True)



    else:
        write("\tLogged in")

        upcomingTestsElement = driver.find_element(By.CLASS_NAME, "qc-registrations-container cb-margin-bottom-32")

        
        try:
            upcomingTestBoxes = upcomingTestsElement.find_elements(By.XPATH, "//*[@role='region']")

            for upcomingTest in upcomingTestBoxes:
                testDateStr = upcomingTest.find_element(By.CLASS_NAME, "cb-roboto-medium qc-registration-display-title").text

        except:
            write("No upcoming tests")

            


        completedTestsElement = driver.find_element(By.CLASS_NAME, "qc-assessment-summary-card-list")

        try:
            scoreBoxes = completedTestsElement.find_elements(By.XPATH, "//*[@role='region']")

            for scoreBox in scoreBoxes:
                try:
                    score = scoreBox.find_element("div",{"class":"cb-roboto-light cb-margin-right-8 cb-font-size-xlarge-res"}).text
                    splits = scoreBox.find_elements("div",{"class":"cb-roboto-light cb-margin-right-8 cb-paragraph4-res"})

                    write("\tSCORE RELEASED! Total score: " + score, True)

                    write("\tReading Score: " + splits[0].text + " | Math Score: " + splits[1].text, True)

                    if int(score) > 1500:
                        write("\tCongrats :3", True)
                    elif int(score) > 1300:
                        write("\tDecent score...", True)
                    else:
                        write("\tASS SCORE", True)
                    
                    #if you want to add some way to notify the user, add it here

                    
                    # driver.close()
                    # done = True
                

                except:
                    write("\t" + time.strftime("%m/%d/%Y") + "@" + time.strftime("%H:%M:%S", time.localtime()) + " | No score, waiting " + str(refreshBuffer) + " seconds before retrying")
                    time.sleep(refreshBuffer)
                    driver.refresh()
                    # '''
        except:
            write("\tError when attempting to retrieve score elements", True)