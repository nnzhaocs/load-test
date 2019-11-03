from locust import HttpLocust, TaskSet, task
from random import randint
import base64
import time
import uuid
               	
counter = 0

class AnonTasks(TaskSet):

	@task
	def loadImage(self):
		catalogue = self.client.get("/catalogue?size=100")
		sizeResponse = self.client.get("/catalogue/size")
		size = sizeResponse.json()["size"]
		index = randint(0, size-1)
		imageUrl = catalogue.json()[index]["imageUrl"][0]
		image = self.client.get(imageUrl)

	@task
	def getTags(self):
		tags = self.client.get("/tags")
		body = tags.json()

class APITasks(TaskSet):
	# def on_start(self):
		# self.login()

	@task
	def purchaseItem(self):
		self.createCustomer()
		self.createCard()
		self.createAddress()
		self.login()
		self.addItemToCart()
		self.buy()
		self.deleteCustomer()
		self.deleteCard()
		self.deleteAddress()

	# @task
	# def addRemoveFromCart(self):
	# 	self.createCustomer()
	# 	self.login()
	# 	self.addItemToCart()
	# 	self.removeItemFromCart()
	# 	self.deleteCustomer()

	def removeItemFromCart(self):
		self.client.delete("/cart/" + self.cart_id + "/items/" + self.item_id)

	# @task
	def addItemToCart(self):

		cart = self.client.get("/cart")
		catalogue = self.client.get("/catalogue?size=100")
		sizeResponse = self.client.get("/catalogue/size")
		size = sizeResponse.json()["size"]
		index = randint(0, size-1)
		catItem = catalogue.json()[index]
		time.sleep(2.0)

		self.item_id = catItem["id"]
		self.client.post("/cart", json={"id": self.item_id, "quantity": 1})

	def buy(self):
		cookie = {'logged_in': self.cust_id}
		self.client.post("/orders", cookies=cookie)

	def login(self):
		base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
		login = self.client.get("/login", headers={"Authorization":"Basic %s" % base64string})
		# self.cust_id = login.cookies["logged_in"]

	def createCustomer(self):
		global counter
		counter += 1
		self.username = "test_user_" + str(uuid.uuid4())

		self.password = "test_password"
		customer = self.client.post("/register", json={"username": self.username, "password": self.password})

		self.cust_id = customer.json()["id"]

	def createCard(self):
		self.client.post("/cards", json={"longNum": "5429804235432", "expires": "04/16", "ccv": "432"})
		card = self.client.post("/cards", json={"longNum": "5429804235432", "expires": "04/16", "ccv": "432", "userId": self.cust_id})
		self.card_id = card.json()["id"]	
	
	def createAddress(self):
		self.client.post("/addresses", json={"street": "my road", "number": "3", "country": "UK", "city": "London"})
		addr = self.client.post("/addresses", json={"street": "my road", "number": "3", "country": "UK", "city": "London", "userId":self.cust_id})
		self.addr_id = addr.json()["id"]

	def deleteCustomer(self):
		self.client.delete("/customers/" + self.cust_id)
	def deleteCard(self):
		self.client.delete("/cards/" + self.card_id)
	def deleteAddress(self):
		self.client.delete("/addresses/" + self.addr_id)

class ErrorTasks(TaskSet):

	def addItemToCart(self):
		cart = self.client.get("/cart")
		catalogue = self.client.get("/catalogue?size=100")
		sizeResponse = self.client.get("/catalogue/size")
		size = sizeResponse.json()["size"]
		index = randint(0, size-1)
		catItem = catalogue.json()[index]
		time.sleep(2.0)
		self.item_id = catItem["id"]
		self.client.post("/cart", json={"id": self.item_id, "quantity": 3})

	@task
	def login_fail(self):
		base64string = base64.encodestring('%s:%s' % ("wrong_user", "no_pass")).replace('\n', '')
		with self.client.get("/login", headers={"Authorization":"Basic %s" % base64string}, catch_response=True) as response:
			if response.status_code == 401:
				response.success()

	@task
	def checkout_fail(self):
		self.addItemToCart()
		with self.client.post("/orders", json={}, catch_response=True) as response:
			if response.status_code == 500:
				response.success()

class LoggedInUser(HttpLocust):
	task_set = APITasks
	min_wait = 2000
	max_wait = 5000

class UnknownUser(HttpLocust):
	task_set = AnonTasks
	min_wait = 2000
	max_wait = 5000

class ErrorUser(HttpLocust):
	task_set = ErrorTasks
	min_wait = 2000
	max_wait = 5000
