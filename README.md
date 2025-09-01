# Dragon's Vault Discord Bot

A Discord bot for managing customer order tickets with role selection, order placement, approval workflow, and ticket management. Built with `discord.py` and hosted on Render for 24/7 uptime.

---

## Features

- Role assignment via reaction (Worker, Customer)
- Order placement through a button and modal input
- Admin approval or cancellation of orders
- Automatic creation of ticket channels for approved orders
- Ticket controls: cancel and complete
- Worker price quoting
- Order logs and order-info channels to track orders

---

## Setup & Deployment

### Prerequisites

- Python 3.10+
- Discord Bot Token
- Discord server with these channels created:
  - `order-requests`
  - `order-logs`
  - `order-info`

### Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/dragons-vault-bot.git
   cd dragons-vault-bot
````

2. Create a `.env` file in the root with:

   ```
   TOKEN=your_discord_bot_token_here
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the bot locally:

   ```bash
   python bot.py
   ```

---

## Commands

| Command          | Description                             | Permission    |
| ---------------- | --------------------------------------- | ------------- |
| `!setup_roles`   | Sends role selection message            | Administrator |
| `!order`         | Sends the "Place Order" button          | Administrator |
| `!complete`      | Completes and closes the current ticket | Administrator |
| `!quote <price>` | Worker quotes a price for the order     | Worker role   |

---

## Hosting on Render

* Add `Flask` as dependency (in `requirements.txt`) to keep the bot process alive.
* Set up a **Web Service** on Render.
* Use the start command: `python bot.py`
* Create environment variable `TOKEN` in Render’s dashboard.
* Your bot will run 24/7 with a free tier Flask webserver to prevent sleeping.

---

## Notes

* Ensure the channels `order-requests`, `order-logs`, and `order-info` exist in your Discord server.
* Bot requires `Administrator` role to manage roles and tickets properly.
* Keep your `.env` file private and include `.env` in `.gitignore`.

---

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.


---

## Contact

For questions or support, open an issue or contact me.

```

If you want, I can help you customize it further or add badges, images, or other sections!
```
