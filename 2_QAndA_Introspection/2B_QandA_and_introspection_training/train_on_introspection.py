"""
Just dummy code to show the concept
"""

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, T5ForConditionalGeneration
import random
import numpy as np

# Initialize model, tokenizer, optimizer
model_name = "Salesforce/codet5p-220m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = T5ForConditionalGeneration.from_pretrained(model_name)
model.to(device)
optimizer = AdamW(model.parameters(), lr=5e-5)
model.train()

# List of programming concepts for q_category_1
programming_concepts = [
    "variables", "loops", "functions", "classes", "inheritance", "recursion",
    "data structures", "sorting algorithms", "search algorithms", "file I/O",
    "exception handling", "concurrency", "network programming", "database connectivity",
    "memory management", "object-oriented programming", "functional programming",
    "lambda expressions", "list comprehensions", "generators", "decorators",
    "regular expressions", "unit testing", "debugging", "design patterns"
]

def compute_reward(is_correct, confidence):
    base_reward = 1 if is_correct else -1
    adjusted_reward = base_reward * (confidence / 10)
    return adjusted_reward

def check_answer_correctness(agent_answer, correct_answer):
    # Simple string comparison (can be replaced with more advanced similarity metrics)
    return agent_answer.strip().lower() == correct_answer.strip().lower()

def tokenize_input(text):
    return tokenizer.encode(text, return_tensors='pt').to(device)

def generate_model_answer(input_ids, max_length=512):
    outputs = model.generate(
        input_ids=input_ids,
        max_length=max_length,
        output_scores=True,
        return_dict_in_generate=True
    )
    model_answer_ids = outputs.sequences
    model_answer = tokenizer.decode(model_answer_ids[0], skip_special_tokens=True)
    return model_answer

def compute_loss_and_reward(input_ids, labels, is_correct, confidence):
    outputs = model(input_ids=input_ids, labels=labels)
    loss = outputs.loss
    reward = compute_reward(is_correct, confidence)
    adjusted_loss = loss * reward
    return adjusted_loss, reward

def perform_backward_pass(loss):
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

def extract_confidence(model_answer):
    if 'Confidence:' in model_answer:
        answer_parts = model_answer.split('Confidence:')
        agent_answer = answer_parts[0].strip()
        try:
            confidence = float(answer_parts[1].strip())
        except ValueError:
            confidence = 5.0  # Default confidence
    else:
        agent_answer = model_answer.strip()
        confidence = 5.0  # Default confidence
    return agent_answer, confidence

def generate_question_and_answer(concept):
    # Placeholder function to generate question-answer pairs
    qa_pairs = {
        "variables": ("What is a variable in programming?", "A variable is a storage location paired with a symbolic name that contains some known or unknown quantity of information referred to as a value."),
        "loops": ("What is a loop in programming?", "A loop is a sequence of instructions that is continually repeated until a certain condition is reached."),
        # Add more predefined questions and answers
    }
    if concept in qa_pairs:
        return qa_pairs[concept]
    else:
        # Default question and answer
        return (f"Explain the concept of {concept} in programming.", f"This is a placeholder answer for the concept of {concept}.")

# Implement q_category_5
def run_q_category_5():
    # Placeholder question text
    question = "Explain the concept of recursion in programming."
    input_text = question

    # Step 1: Have the model generate its own answer
    input_ids = tokenize_input(input_text)
    model_answer = generate_model_answer(input_ids, max_length=50)
    # Ensure the model's answer is limited to 30 tokens
    model_answer_tokens = tokenizer.tokenize(model_answer)[:30]
    model_answer = tokenizer.convert_tokens_to_string(model_answer_tokens)

    # Step 2: Create dummy answers
    dummy_answers = [
        "Recursion is when a function calls itself to solve smaller instances of the same problem.",
        "Recursion is a method of solving problems by repeating identical or similar processes.",
        "In programming, recursion is a technique where a function calls itself directly or indirectly."
    ]
    # Insert the model's own answer into the options
    options = dummy_answers + [model_answer]
    random.shuffle(options)

    # Present the options to the model
    options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    input_text = f"Was output O generated by agent [T5NAME]? Here is output O:\n{model_answer}\n\nOptions:\n{options_text}\n\nSelect the option that was generated by agent [T5NAME]."

    # Tokenize the input
    input_ids = tokenize_input(input_text)

    # The correct answer is the index of the model's own answer in the shuffled options
    correct_option_index = options.index(model_answer)
    correct_answer_text = str(correct_option_index + 1)  # Options are 1-indexed

    # Get the model's selection
    model_selection = generate_model_answer(input_ids, max_length=10)
    agent_answer, confidence = extract_confidence(model_selection)

    # Check if the model selected the correct option
    is_correct = agent_answer.strip() == correct_answer_text.strip()

    # Compute loss and reward
    labels = tokenizer.encode(correct_answer_text, return_tensors='pt').to(device)
    adjusted_loss, reward = compute_loss_and_reward(input_ids, labels, is_correct, confidence)

    # Perform backward pass
    perform_backward_pass(adjusted_loss)

    print(f"q_category_5 | Is Correct: {is_correct} | Confidence: {confidence} | Reward: {reward}")
    return adjusted_loss.item(), reward

# Update other category functions to return loss and reward
def run_q_category_1():
    # q_category_1 implementation
    concept = random.choice(programming_concepts)
    question, correct_answer = generate_question_and_answer(concept)
    input_text = f"Does agent [T5NAME] know the answer to question {question}?"
    input_ids = tokenize_input(input_text)
    # Get the model's answer
    model_answer = generate_model_answer(input_ids)
    agent_answer, confidence = extract_confidence(model_answer)
    is_correct = check_answer_correctness(agent_answer, correct_answer)
    # Compute loss and reward
    labels = tokenizer.encode(correct_answer, return_tensors='pt').to(device)
    adjusted_loss, reward = compute_loss_and_reward(input_ids, labels, is_correct, confidence)
    # Perform backward pass
    perform_backward_pass(adjusted_loss)
    print(f"q_category_1 | Is Correct: {is_correct} | Confidence: {confidence} | Reward: {reward}")
    return adjusted_loss.item(), reward

def run_q_category_8():
    # q_category_8 implementation
    strings = [
        "Hello world!",
        "The quick brown fox jumps over the lazy dog.",
        "In programming, a function is a block of code that performs a specific task.",
        "To be or not to be, that is the question.",
        # Add more strings
    ]
    string = random.choice(strings)
    question = f"How many tokens are in this string: {string}?"
    input_ids = tokenize_input(question)
    # Get the model's answer
    model_answer = generate_model_answer(input_ids, max_length=20)
    agent_answer_text, confidence = extract_confidence(model_answer)
    try:
        agent_answer = int(agent_answer_text)
    except ValueError:
        agent_answer = None
    num_tokens = len(tokenizer.encode(string, add_special_tokens=False))
    is_correct = (agent_answer == num_tokens)
    # Compute loss and reward
    labels = tokenizer.encode(str(num_tokens), return_tensors='pt').to(device)
    adjusted_loss, reward = compute_loss_and_reward(input_ids, labels, is_correct, confidence)
    # Perform backward pass
    perform_backward_pass(adjusted_loss)
    print(f"q_category_8 | Is Correct: {is_correct} | Confidence: {confidence} | Reward: {reward}")
    return adjusted_loss.item(), reward

def run_q_category_10():
    # q_category_10 implementation
    prompt = "The quick brown fox"
    question = f"What is the probability of the first 5 logits for each of the following continued words?"
    input_text = f"{prompt}\n{question}"
    input_ids = tokenize_input(prompt)
    # Get logits
    with torch.no_grad():
        outputs = model(input_ids=input_ids)
        logits = outputs.logits
    next_token_logits = logits[:, -1, :]
    probs = torch.softmax(next_token_logits, dim=-1)
    top_probs, top_indices = torch.topk(probs, k=5, dim=-1)
    top_tokens = [tokenizer.decode([idx]) for idx in top_indices[0]]
    top_probs = top_probs[0].cpu().numpy()
    model_expected_answer = ""
    for token, prob in zip(top_tokens, top_probs):
        model_expected_answer += f"Token: {token}, Probability: {prob:.4f}\n"
    # Ask the model
    input_ids = tokenize_input(input_text)
    model_answer = generate_model_answer(input_ids)
    agent_answer, confidence = extract_confidence(model_answer)
    is_correct = (agent_answer.strip() == model_expected_answer.strip())
    # Compute loss and reward
    labels = tokenizer.encode(model_expected_answer, return_tensors='pt').to(device)
    adjusted_loss, reward = compute_loss_and_reward(input_ids, labels, is_correct, confidence)
    # Perform backward pass
    perform_backward_pass(adjusted_loss)
    print(f"q_category_10 | Is Correct: {is_correct} | Confidence: {confidence} | Reward: {reward}")
    return adjusted_loss.item(), reward

# Placeholder functions for other categories (updated to return loss and reward)
def run_q_category_2():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

def run_q_category_3():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

def run_q_category_4():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

def run_q_category_6():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

def run_q_category_7():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

def run_q_category_9():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

def run_q_category_11():
    # Placeholder implementation
    loss = torch.tensor(0.0)
    reward = 0.0
    return loss.item(), reward

# Main training loop
num_iterations = 50
q_categories = list(range(1, 12))  # Categories 1 to 11

for iteration in range(num_iterations):
    print(f"Iteration {iteration+1}/{num_iterations}")
    q_category = random.choice(q_categories)
    if q_category == 1:
        loss, reward = run_q_category_1()
    elif q_category == 2:
        loss, reward = run_q_category_2()
    elif q_category == 3:
        loss, reward = run_q_category_3()
    elif q_category == 4:
        loss, reward = run_q_category_4()
    elif q_category == 5:
        loss, reward = run_q_category_5()
    elif q_category == 6:
        loss, reward = run_q_category_6()
    elif q_category == 7:
        loss, reward = run_q_category_7()
    elif q_category == 8:
        loss, reward = run_q_category_8()
    elif q_category == 9:
        loss, reward = run_q_category_9()
    elif q_category == 10:
        loss, reward = run_q_category_10()
    elif q_category == 11:
        loss, reward = run_q_category_11()
    else:
        print(f"Invalid q_category: {q_category}")
        continue
    print(f"Loss: {loss:.4f} | Reward: {reward:.4f}")