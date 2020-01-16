# First written by Wang Weizhuo, March 2018
# V4.1 modified for spring 2019 semester, Integrated CRN
# V4.2 Minor fixes, start logging changes
# V4.3 Added Class drop features
# Version V3.1 distributed on 2018/5/13 to Tony Li
# Version V4.2 distributed on 2019/1/12 to Mickey
# Version V4.3 distributed on 2019/1/14 to Mickey.
# Version V4.3.2 distributed on 2019/1/15 to CYX, Mickey. with relogin bug patch
# Version V4.4 Speed up by pre lauching browser, distributed to Mickey.
# Version V4.5 Spring 2020 update.


from selenium import webdriver , common
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.support.ui import Select
import time  
import imaplib
import os

def init_browser():
	# ========Open Browser===========
	print ''
	options = webdriver.ChromeOptions()
	# options.add_argument('--headless')
	# options.add_argument('--hide-scrollbars')
	# options.add_argument('--disable-gpu')
	options.add_argument("--log-level=3")  # fatal
	driver = webdriver.Chrome(chrome_options=options)
	driver.get("https://webprod.admin.uillinois.edu/ssa/servlet/SelfServiceLogin?appName=edu.uillinois.aits.SelfServiceLogin&dad=BANPROD1")  

	# ========Login to system========
	#password and username
	elem_user = driver.find_element_by_name("USER")
	elem_user.send_keys(netid[0])
	elem_pwd = driver.find_element_by_name("PASSWORD")
	elem_pwd.send_keys(netid[1])
	elem_pwd.send_keys(Keys.RETURN)

	return driver

def gotoPREAdd(driver,delay):
	#go to reg & rec page
	while True:
		try:
			nextpage = driver.find_element_by_partial_link_text("Regis")
		except common.exceptions.NoSuchElementException:
			pass
		else:
			time.sleep(delay)
			nextpage.click()
			break

	print("Navigated to Regis")

	#go to classic registration page
	while True:
		try:
			nextpage = driver.find_element_by_partial_link_text("Classic")
		except common.exceptions.NoSuchElementException:
			pass
		else:
			time.sleep(delay)
			nextpage.click()
			break

	print("Navigated to classic")

	#go to classic add drop page
	while True:
		try:
			nextpage = driver.find_element_by_partial_link_text("Add")
		except common.exceptions.NoSuchElementException:
			pass
		else:
			time.sleep(delay)
			nextpage.click()
			break

def gotoAdd(driver,delay):

	print("Navigated to add drop")
	#go to classic add drop page
	while True:
		try:
			nextpage = driver.find_element_by_partial_link_text("I Agree")
		except common.exceptions.NoSuchElementException:
			pass
		else:
			time.sleep(delay)
			nextpage.click()
			break

	print("Navigated to agreed")

	#go to spring 2018
	while True:
		try:
			dropdown = driver.find_element_by_xpath('//*[@id="term_id"]')
			selectTerm = Select(dropdown)
			# Magic rule to select semester: 120 + year + x
			# year: 18 19 20 etc
			# x   : | 0 - Winter | 1 - Spring | 5 - Summer | 8 - Fall |
			selectTerm.select_by_value("120201")					
			nextpage = driver.find_element_by_xpath("//input[@value='Submit'][@type='submit']")
		except common.exceptions.NoSuchElementException:
			pass
		else:
			time.sleep(delay)
			nextpage.click()
			break

	time.sleep(1)
	print("Successfully got in the add/drop page")

def LogInGmail(user,password):
	# ==========Login Gmail==========
	print '\nLogging into gmail'
	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(user,password)
	mail.list()
	mail.select(folder)
	return mail

def CheckEmail(mail,freq,i):
	time.sleep(freq)
	mail.select(folder)

	# CRN 1 
	result, data = mail.search(None, '(BODY "'+'55128'+'")')
	ids = data[0]
	id_list = ids.split()
	newsize1 = len(id_list)

	# CRN2
	result, data = mail.search(None, '(BODY "'+'63422'+'")')
	ids = data[0]
	id_list = ids.split()
	newsize2 = len(id_list)

	newsize = newsize1 + newsize2

	# Re login every 3 hours
	if (i*freq)%(3*3600) == 0:
		mail.logout()
		mail = LogInGmail(gmail[0],gmail[1])
		print 'Logged Again'
	# print 'size = ',size
	# print 'time:',i*freq,'/',checktime
	print '\rUp time:',(i*freq/3600),'hour',(i*freq/60)%60,'min',(i*freq)%60,'seconds',
	if newsize == size:
		return mail,False
	else:
		print '\nFound! Inbox size:',newsize,' time:',i*freq
		print 'Launching browser to register'
		return mail,True

def autoRegister(driver,netid,delay):

	gotoAdd(driver,delay)

	# =======Check before register======
	try:
		reg = driver.find_element_by_xpath("//input[@name='CRN_IN' and @value='"+CRN+"']")
	except common.exceptions.NoSuchElementException:
		registered = False
	else:
		registered = True

	print 'Registered ',CRN,'? ',registered


	if not registered:
		print 'Continue to register ',CRN
		# Put CRN in box
		CRNreg = driver.find_element_by_xpath("//input[@id='crn_id1']")
		CRNreg.send_keys('55128')
		CRNreg = driver.find_element_by_xpath("//input[@id='crn_id2']")
		CRNreg.send_keys('63422')
		# Drop the class
		try:
			dropdown = driver.find_element_by_xpath("//input[@name='CRN_IN' and @value='"+CRNdrop+"']/../../td[2]/select[1]")
		except common.exceptions.NoSuchElementException:
			print 'Did not found CRN '+CRNdrop+' to drop. Skipping...'
		else:
			drop = Select(dropdown)
			drop.select_by_value("DW")	

		# Click submit
		nextpage = driver.find_element_by_xpath("//input[@name='REG_BTN'][@value='Submit Changes'][@type='submit']")
		nextpage.click()
		try:
			ErrorBlock = driver.find_element_by_class_name("errortext") 
		except common.exceptions.NoSuchElementException:
			print("!!!!!!!!!!!!!!!!!!!!!!!")
			print("!!!!!===SUCCESS===!!!!!")
			print("!!!!!!!!!!!!!!!!!!!!!!!")
			print("Registered: "+CRN)
			print("   Dropped: "+CRNdrop)
			success = True
		else:
			error = driver.find_element_by_xpath("/html/body/div[3]/form/table[4]/tbody/tr[2]/td[1]")
			print "CRN: "+CRN+" Error Message: "+error.text
			success = False

	# ==========Exiting=============
	ff = raw_input('Done.Press enter to quit.')
	# driver.close()
	try:
		driver.quit()
	except common.exceptions.SessionNotCreatedException:
		pass
	else:
		pass

def AskInfo():
	os.system('cls')
	netid    = ['','']
	print '\n Auto Register V4.5 \n'
	print '\n    ****Check befor you run****\n'
	conti    = raw_input("Have you forward alert mail from your school mail to expcourse@gmail.com? (y/n)")
	if conti != 'y':
		print 'You have to set up the email before you use this script'
		return False,False,False
	print '\n    ****Directions****\n'
	print '|You need to leave this window open in order to auto register for classes.'
	print '|Your password will NOT be saved, it will be asked every time this script is run.\n'
	print '|| Enter 0 if you dont wish to drop any course.\n'
	# CRN      = raw_input("Course CRN to register: ")
	CRN = '55128'
	CRNdrop  = raw_input("    Course CRN to drop: ")
	netid[0] = raw_input("            Your NetID: ")
	netid[1] = raw_input("    Password for NetID: ")

	os.system('cls')
	print '\n    ****Registering****\n'

	return netid,CRN,CRNdrop

def checkAlive(driver):
	driver.get("https://webprod.admin.uillinois.edu/ssa/servlet/SelfServiceLogin?appName=edu.uillinois.aits.SelfServiceLogin&dad=BANPROD1")  
	if "As a security precaution, never click e-mail or instant messenger" in driverobj.page_source:
		pass
	else:
		print("Browser Not alive, re logging in.")
		# ========Login to system========
		#password and username
		elem_user = driver.find_element_by_name("USER")
		elem_user.send_keys(netid[0])
		elem_pwd = driver.find_element_by_name("PASSWORD")
		elem_pwd.send_keys(netid[1])
		elem_pwd.send_keys(Keys.RETURN)
	gotoPREAdd(driver,delay)



# How to use this?
# 
# 1.Make sure you have a gmail
# 2.Create a new label in gmail named 'course'
# 3.Go to courses.illinois.edu, add your CRN to favorite (one at a time) 
# 	and enable email notification
# 4.Set up the settings below and you are good to go

# ===========Settings============
# checktime = 3600*5; 						  # Or set a time to stop
freq = 3;       							  # Check email every ?
delay = 0.01   								  # Page click latency
folder = "wwz"							  # Gmail folder to check
gmail = ['expcourse@gmail.com','Ww147852369'] # Gmail account
netid,CRN,CRNdrop = AskInfo()
if netid == False:
	exit()

# ==========Initialize===========
# Email
mailobj = LogInGmail(gmail[0],gmail[1])
result, data = mailobj.search(None, '(BODY "'+'55128'+'")')
ids = data[0] 								  # data is a list.
id_list = ids.split() 						  # ids is a space separated string
size1 = len(id_list) 						  # get the latest

result, data = mailobj.search(None, '(BODY "'+'63422'+'")')
ids = data[0] 								  # data is a list.
id_list = ids.split() 						  # ids is a space separated string
size2 = len(id_list) 						  # get the latest

size = size1 + size2

print 'Inbox size:',size
print 'Checking for:',CRN
found = False
i = 1;

# Browser
print("\nPre-Lauching Browser")
driverobj = init_browser()
gotoPREAdd(driverobj,delay)
# print(driverobj.page_source().contains("As a security precaution, never click e-mail"))
# print("I understand that the University is advancing" in driverobj.page_source)

# =========Check Email=============
print '\nYou may terminate this bot at any time using Ctrl+C\n'
while (not found):# and (i<=checktime/freq):
	mailobj,found = CheckEmail(mailobj,freq,i)
	i+=1
	# Re login every 30 mins
	if (i*freq)%(1200) == 0:
		checkAlive(driverobj)

if found:
	autoRegister(driverobj,netid,delay)
else:
	print "Not Found in designated time slots!"
