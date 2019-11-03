from locust import HttpLocust, TaskSet, task
from random import randint
import base64
import time
import uuid
               	
counter = 0

class APITasks(TaskSet):
	
	@task
	def purchaseItem(self):
		self.createCustomer()
	#	self.createCard()
	#	self.createAddress()
		self.login()
	#	self.addItemToCart()
	#	self.buy()
#		self.deleteCustomer()
#		self.deleteCard()
#		self.deleteAddress()

	@task
	def addRemoveFromCart(self):
	 	self.createCustomer()
	 	self.login()
	# 	self.addItemToCart()
	# 	self.removeItemFromCart()
#	 	self.deleteCustomer()

	def login(self):
		base64string = base64.encodestring('%s:%s' % ('user', 'password')).replace('\n', '')
		login = self.client.get("/login", headers={"Authorization":"Basic %s" % base64string})
		# self.cust_id = login.cookies["logged_in"]

	def createCustomer(self):
		global counter
		counter += 1
		self.username = "test_user_" + str(uuid.uuid4())

		self.password = "test_password"
		customer = self.client.post("/customers", json={"username": self.username, "password": self.password})
		#print customer
		#self.cust_id = customer.json()["id"]

	#def createCard(self):
	#	self.client.post("/cards", json={"longNum": "5429804235432", "expires": "04/16", "ccv": "432"})
	#	card = self.client.post("/cards", json={"longNum": "5429804235432", "expires": "04/16", "ccv": "432", "userId": self.cust_id})
	#	print card
	#	#self.card_id = card.json()["id"]	

	#def createAddress(self):
	#	self.client.post("/addresses", json={"street": "my road", "number": "3", "country": "UK", "city": "London"})
	#	addr = self.client.post("/addresses", json={"street": "my road", "number": "3", "country": "UK", "city": "London", "userId":self.cust_id})
	#	print addr
		#self.addr_id = addr.json()["id"]

	#def deleteCustomer(self):
	#	self.client.delete("/customers/" + self.cust_id)

	#def deleteCard(self):
	#	self.client.delete("/cards/" + self.card_id)

	#def deleteAddress(self):
	#	self.client.delete("/addresses/" + self.addr_id)

class ErrorTasks(TaskSet):

	@task
	def login_fail(self):
		base64string = base64.encodestring('%s:%s' % ("wrong_user", "no_pass")).replace('\n', '')
		with self.client.get("/login", headers={"Authorization":"Basic %s" % base64string}, catch_response=True) as response:
			if response.status_code == 401:
				response.success()


class LoggedInUser(HttpLocust):
	task_set = APITasks
	min_wait = 2000
	max_wait = 5000

class ErrorUser(HttpLocust):
	task_set = ErrorTasks
	min_wait = 2000
	max_wait = 5000
