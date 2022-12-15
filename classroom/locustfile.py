from locust import HttpUser, TaskSet, task, between


class UserActions(TaskSet):

    def on_start(self):
        pass

    @task(1)
    def index(self):
        self.client.get('/classrooms/?faculty_id=1')


class ApplicationUser(HttpUser):
    tasks = [UserActions]
    host = "http://127.0.0.1:8000"

    wait_time = between(0, 1)
