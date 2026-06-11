from locust import HttpUser, task, between


class AnonymousUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://school-might-marathon.ru"

    @task
    def visit_home(self):
        self.client.get("/")
