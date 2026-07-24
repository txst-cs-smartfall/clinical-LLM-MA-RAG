# app/llm.py
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from dotenv import load_dotenv
import os

load_dotenv()
HF_key = os.getenv("HF_TOKEN")
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_key)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    dtype=torch.float16
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=1200,
    do_sample=False,
    repetition_penalty=1.1,
    return_full_text=True
)

def call_llm(system_msg: str, user_msg: str) -> str:
    prompt = (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n"
        f"{system_msg}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n"
        f"{user_msg}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n"
    )
    raw = pipe(prompt)[0]["generated_text"]
    marker = "<|start_header_id|>assistant<|end_header_id|>"
    answer = raw.split(marker)[-1].strip() if marker in raw else raw[len(prompt):].strip()
    return answer.replace("<|eot_id|>", "").strip()


# ── LLM Helper ─────────────────────────────────────────────
def call_llm(system_msg: str, user_msg: str) -> str:

    prompt = (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n"
        f"{system_msg}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n"
        f"{user_msg}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n"
    )

    raw = pipe(prompt)[0]["generated_text"]

    marker = "<|start_header_id|>assistant<|end_header_id|>"

    if marker in raw:
        answer = raw.split(marker)[-1].strip()
    else:
        answer = raw[len(prompt):].strip()

    answer = answer.replace("<|eot_id|>", "").strip()

    return answer