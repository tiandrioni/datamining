import requests
import json
from pathlib import Path
from fake_headers import Headers


class GitHubUserRepos:
    headers = Headers(headers=True).generate()

    def __init__(self, user_name):
        self.user_name = user_name
        self.url = f'https://api.github.com/users/{user_name}/repos'

    def save_repos(self):
        file = Path(__file__).parent.joinpath(f'{self.user_name}_repos.json')
        file.write_text(json.dumps(self.repos))
        print(f'Информация по репозиториям пользователя {self.user_name} сохранена в файл {self.user_name}_repos.json')

    def get_repos(self):
        req = requests.get(self.url)
        self.repos = req.json()
        repos_list = []
        for repo in self.repos:
            repos_list.append(repo['name'])
        return repos_list

    def run(self):
        print(self.get_repos())
        self.save_repos()


def run():
    atmos_repos = GitHubUserRepos('atmos')
    atmos_repos.run()


run()

