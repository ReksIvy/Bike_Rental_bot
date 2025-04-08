# 🛵 Telegram Bike Rental Bot

A Telegram bot that streamlines motorcycle rental orders by allowing clients to book a bike, choose a rental period, and submit their personal information — all directly in the chat. Once an order is placed, it’s saved to the database, and owner gets a notification with all details.

---

## ✨ Features

- ✅ Browse available motorcycles for rent
- 📆 Select rental duration (start and end date)
- 🧾 Submit personal information via guided form
- 🗃️ Store data in a structured database
- 🔔 Real-time notification to the owner when an order is placed
- 🔐 Input validation for data consistency and security

---

## 🎯 Purpose

This project is part of my personal portfolio to demonstrate my skills in:

- Building real-world Telegram bots
- Integrating user-friendly chat workflows
- Handling form-style input within conversational interfaces
- Connecting bots with persistent databases
- Automating business operations

---

## 🛠️ Built With

- **Python** — core language
- **python-telegram-bot** — for building Telegram bot interactions
- **SQL Express** — to store data (configurable)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - for image processing
- **Logging & error handling** — for smooth production use

---

## Example Usage
The bot greets the user and if the user is new it prompts the user to choose a language, languages can be easily added to the bot.

Below is the main menu of the bot:

![image](https://github.com/user-attachments/assets/c8499570-ed4c-4c79-bd22-29b421f7dec5)

An example list of available for rent motorcycles:

![image](https://github.com/user-attachments/assets/99f2e260-ccea-4444-a811-bec81bbb3ef0)

An example of user interaction with the bot when forming an order:

![image](https://github.com/user-attachments/assets/653b2a0c-77e9-4dae-a87c-cfe80e91516f)

An example of order details before confirmation:

![image](https://github.com/user-attachments/assets/e131e83f-0c87-43cf-af7c-b6d5a35bf47c)
