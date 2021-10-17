import random

from locust import HttpUser, task, between


class IndexLoading(HttpUser):
    wait_time = between(5, 9)

    @task
    def get_orders(self):
        self.client.get("http://127.0.0.1:8000/orders/")

    @task
    def create_order(self):
        order_id_list = ["u12rT", "op5jk", "iim7f", "456er", "po787"]
        status_list = ["processing", "in_progress", "delivered"]
        for _ in range(10):
            random_order_id = random.choice(order_id_list)
            random_status_list = random.choice(status_list)
            self.client.post(
                "http://127.0.0.1:8000/orders",
                json={"order_id": random_order_id, "status": random_status_list},
            )
