import os
import yaml
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel
from trl import SFTTrainer

# Set logging
logging.set_verbosity_info()

def load_config(config_path="training/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def train():
    config = load_config()
    
    print(f"Loading model: {config['model_name']}")
    
    # Quantization Config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config['load_in_4bit'],
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )

    # Load Model (Mocking for protocol if no GPU/Model access)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            config['model_name'],
            quantization_config=bnb_config,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
        tokenizer.pad_token = tokenizer.eos_token
    except Exception as e:
        print(f"Warning: Could not load actual model ({e}). Running in MOCK mode for protocol demonstration.")
        return mock_train_loop(config)

    # LoRA Config
    peft_config = LoraConfig(
        lora_alpha=config['lora_alpha'],
        lora_dropout=config['lora_dropout'],
        r=config['lora_r'],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=config['target_modules']
    )

    # Load Dataset
    dataset = load_dataset("json", data_files=config['data_path'], split="train")
    
    # Training Arguments
    training_args = TrainingArguments(
        output_dir=config['output_dir'],
        num_train_epochs=config['num_train_epochs'],
        per_device_train_batch_size=config['per_device_train_batch_size'],
        gradient_accumulation_steps=config['gradient_accumulation_steps'],
        optim=config['optim'],
        save_steps=config['save_steps'],
        logging_steps=config['logging_steps'],
        learning_rate=config['learning_rate'],
        weight_decay=0.001,
        fp16=True,
        bf16=False,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="constant",
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="text", # Assuming dataset has 'text' field or we format it
        max_seq_length=config['max_seq_length'],
        tokenizer=tokenizer,
        args=training_args,
        packing=False,
    )

    print("Starting training...")
    trainer.train()
    print("Training complete.")
    
    trainer.model.save_pretrained(config['output_dir'])

def mock_train_loop(config):
    """
    Simulates the training loop output for demonstration.
    """
    print("Initializing QLoRA adapters...")
    print(f"Target modules: {config['target_modules']}")
    print(f"Loading dataset from {config['data_path']}...")
    
    import time
    epochs = config['num_train_epochs']
    steps_per_epoch = 10
    
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        for step in range(steps_per_epoch):
            loss = 2.5 - (epoch * 0.5) - (step * 0.05) # Simulated loss reduction
            print(f"Step {step+1}/{steps_per_epoch} | Loss: {loss:.4f}")
            time.sleep(0.1)
            
    print(f"Saving adapter weights to {config['output_dir']}...")
    if not os.path.exists(config['output_dir']):
        os.makedirs(config['output_dir'])
    with open(os.path.join(config['output_dir'], "adapter_config.json"), "w") as f:
        json.dump({"lora_alpha": config['lora_alpha'], "r": config['lora_r']}, f)
        
    print("Mock training complete.")

if __name__ == "__main__":
    import json
    train()
