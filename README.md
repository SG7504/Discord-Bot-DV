# 🐉 Dragon's Vault Discord Bot

A full-featured Discord bot built for a guild-based marketplace server where users can act as Customers or Workers. The bot handles role assignment, order requests, ticket creation, admin approval, and transparent order fulfillment.

---

## ✨ Features

- 🔧 **Role Selection**: Members choose between `Worker 🟦` and `Customer 🟩` via reaction roles.
- 📩 **Ticket System**: Customers can open order tickets describing what they need.
- ✅ **Admin Workflow**: Admins have buttons to Approve, Cancel, or Complete tickets.
- 🔒 **Secure Payments**: Workers fulfill orders, and customers pay after admin approval.
- 📜 **Logging**: Every order is logged for transparency in a dedicated admin-only channel.

---

## 📁 Project Structure
├── bot.py / main.py # Main bot logic
├── keep_alive.py # Optional Flask server (not currently active)
├── requirements.txt # Project dependencies
├── .env # Stores secret token
└── README.md # You're reading it!


---

## 🔐 Environment Variables

This project uses a `.env` file to securely manage secrets.

| Key       | Description              |
|-----------|--------------------------|
| `TOKEN`   | Your Discord bot token   |

> ⚠️ Never commit your `.env` file or token to GitHub.

---

## 🧠 Technologies Used

- **Python**
- **discord.py**
- **Flask** (optional)
- **GitHub**

---

## 📜 License

This project is open source and free to use under the [MIT License](LICENSE).

---

## 🤝 Contributing

PRs and suggestions welcome! Feel free to fork the repo and improve the bot.

