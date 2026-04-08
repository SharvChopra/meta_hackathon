import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer
from datasets import Dataset

from github_env import CloudGitHubEnv

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.bfloat16
)

# This must be changed to the ngrok/localtunnel URL when running in Colab
TUNNEL_URL = "http://localhost:5173"
env = CloudGitHubEnv(base_url=TUNNEL_URL)

def browser_reward(prompts, completions, **kwargs):
    rewards = []
    
    for guess_text in completions:
        env.reset_game()
        
        action = str(guess_text).strip()
        
        _, score = env.step(action)
        rewards.append(score)
        
    return rewards

dataset = Dataset.from_dict({
    "prompt": ["You are an AI repository maintainer. Look at the accessibility tree and output the exact BrowserGym command to resolve the issue."] * 1000
})

training_args = GRPOConfig(
    output_dir="./trained-agent",
    learning_rate=1e-5,
    per_device_train_batch_size=2,
    logging_steps=10,
    max_completion_length=100
)

trainer = GRPOTrainer(
    model=model,
    reward_funcs=browser_reward,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()

trainer.save_model("./trained-agent-final")
tokenizer.save_pretrained("./trained-agent-final")
