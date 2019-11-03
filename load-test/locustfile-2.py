import base64

from locust import HttpLocust, TaskSet, task
from random import randint, choice


class WebTasks(TaskSet):

    @task
    def load(self):
        base64string = base64.encodestring('%s:%s' % ('user', 'password')).replace('\n', '')

        self.client.get("/")
        self.client.get("/login", headers={"Authorization":"Basic %s" % base64string})        
        

class Web(HttpLocust):
    task_set = WebTasks
    min_wait = 0
    max_wait = 0
