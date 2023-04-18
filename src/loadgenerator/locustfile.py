from locust import HttpUser, TaskSet, task, between
from random import randint, choice


class WebTasks(TaskSet):
    @task
    def load(self):
        id = randint(1,999)
        self.client.get(f"/user/{id}")


class Web(HttpUser):
    tasks = [WebTasks]
    wait_time = between(0.1,0.5)