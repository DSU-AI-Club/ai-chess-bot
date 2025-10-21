## AI Chess Competition: Participant Guide

Welcome to the AI Chess Competition! This guide tells you the rules, resources, and technicalities for developing and submitting your AI chess engine. The final competition will take place at [Nanocon](https://sites.google.com/view/dsunanocon/events/sunday?authuser=0)!

## 1. General Rules
* Team Size: 1-3 people
* Signup: [this google form]()
* Contact: for any questions, issues, or clarifications, reach out to one of the AI Club officers or Eddie French on Discord
* Do not just clone GitHub repositories or do any form of plagiarism!

## 2. Materials Provided
A Python module will be provided containing:
* requirements file (with the allowed python libraries)
* boilerplate code
* Opening Database (covering opening moves and/or end moves) to integrate into your engine
* Chess Database for training or reference
* Chess Rules PDF will be provided for reference on standard rules of play (e.g., castling, en passant, draw conditions)
* Supplementary **videos** and an **intro to allowed libraries** may be provided to help new participants get started.

## 3. Submission Guidelines
* All submissions must be written in Python
* The only allowed libraries:
    * `numpy`
    * `scikit-learn`
    * `keras`
    * `Pytorch`
    * `tensorflow`
    * `pandas`
    * `python-chess`
* No `import async` please!
* Submission deadline: **Thursday, November 6th, 11:59 pm**
* Submission format: submit python scripts (named `__main__.py` for inference and `__train__.py` for training) via Discord to 
* Final Competition Date: **Sunday, November 9th, 10:00 am**, at Dakota Playhouse

## 4. Engine Parameters and Training
* **Chess Engine:** You need to implement a functional **Chess engine** using the allowed libraries.
* **Hyperparameters:** Be prepared to detail and tune your model's **Hyperparameters**.
* **Depth:** The **search depth** of your engine is a critical factor and must be optimized within the time constraints.
* **Handling Training:** Your submission script will be run on the specified hardware. Ensure your training process is integrated or your model is pre-trained and saved.
* **Handling Inference:** Your script must be optimized for fast and efficient **inference** during the match.

## 5. Hardware and Time Constraints
* **Hardware Specs:** 
* **Time Limit:** 

## 6. After Competition Period
* After the competition concludes, teams will be required to prepare and deliver a presentation on methodology, explaining your algorithm, training process, and time management strategies.
* **Award:** The winning team will receive a **Raspberry Pi 4 kit**!

**Have fun!**