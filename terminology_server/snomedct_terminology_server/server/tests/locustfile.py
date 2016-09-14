from locust import HttpLocust, TaskSet, task


class ListEndpointTaskSet(TaskSet):

    @task
    def list_concepts(self):
        self.client.get('terminology/concepts')

    @task
    def list_descriptions(self):
        self.client.get('terminology/descriptions')

    @task
    def list_relationships(self):
        self.client.get('terminology/relationships')

    @task
    def list_language_refsets(self):
        self.client.get('terminology/refset/language')

    @task
    def list_top_level_concepts(self):
        self.client.get('terminology/concepts/top_level')


class StressTest(HttpLocust):
    task_set = ListEndpointTaskSet
    min_wait = 5000
    max_wait = 15000
