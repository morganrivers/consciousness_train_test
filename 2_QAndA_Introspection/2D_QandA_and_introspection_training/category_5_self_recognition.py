# q_category_5.py

import random
from shared_utils import (
    tokenize_input,
    generate_model_answer,
    extract_confidence,
    compute_loss_and_reward,
    perform_backward_pass
)

def run_q_category_5(agent):
    # Placeholder question text
    question = "Explain the concept of recursion in programming."
    input_text = question

    # Step 1: Have the model generate its own answer
    input_ids = tokenize_input(input_text, agent.tokenizer, agent.device)
    model_answer = generate_model_answer(agent.model, agent.tokenizer, input_ids, max_length=50)
    # Ensure the model's answer is limited to 30 tokens
    model_answer_tokens = agent.tokenizer.tokenize(model_answer)[:30]
    model_answer = agent.tokenizer.convert_tokens_to_string(model_answer_tokens)

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
    input_ids = tokenize_input(input_text, agent.tokenizer, agent.device)

    # The correct answer is the index of the model's own answer in the shuffled options
    correct_option_index = options.index(model_answer)
    correct_answer_text = str(correct_option_index + 1)  # Options are 1-indexed

    # Get the model's selection
    model_selection = generate_model_answer(agent.model, agent.tokenizer, input_ids, max_length=10)
    agent_answer, confidence = extract_confidence(model_selection)

    # Check if the model selected the correct option
    is_correct = agent_answer.strip() == correct_answer_text.strip()

    # Compute loss and reward
    labels = agent.tokenizer.encode(correct_answer_text, return_tensors='pt').to(agent.device)
    adjusted_loss, reward = compute_loss_and_reward(agent.model, input_ids, labels, is_correct, confidence)

    # Perform backward pass
    perform_backward_pass(agent.optimizer, adjusted_loss)

    print(f"q_category_5 | Is Correct: {is_correct} | Confidence: {confidence} | Reward: {reward}")
    return adjusted_loss.item(), reward
