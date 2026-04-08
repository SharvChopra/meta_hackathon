import browsergym.core
import requests
import time

class CloudGitHubEnv:
    def __init__(self, base_url):
        self.env = browsergym.core.Env()
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        
    def reset_game(self):
        response = requests.post(self.api_url + "/reset")
        response.raise_for_status()
        scenario = response.json().get('scenario', {})
        
        difficulty = scenario.get('difficulty')
        
        if difficulty == 'easy':
            path = '/issues/easy'
        elif difficulty == 'medium':
            path = '/issues/medium'
        elif difficulty == 'hard':
            path = '/pulls/hard'
        else:
            path = '/'
            
        target_url = self.base_url + path
        
        obs, _ = self.env.reset(url=target_url)
        return obs['axtree_txt']
        
    def step(self, action_cmd):
        try:
            obs, _, _, _, _ = self.env.step(action_cmd)
            
            time.sleep(1.5)
            
            grade_resp = requests.get(self.api_url + "/grade")
            grade_resp.raise_for_status()
            score = grade_resp.json().get('score', -0.5)
            
        except Exception as e:
            obs = {'axtree_txt': 'Execution Error'}
            score = -0.5
            
        return obs['axtree_txt'], score
