# Codeforces Discord Bot

A Discord bot that links Codeforces accounts to Discord users, manages roles based on ratings, and notifies about upcoming contests.

## Features

- **Link Account**: Link your Codeforces handle to your Discord account.
- **Auto Roles**: Automatically updates your Discord role based on your Codeforces rating (e.g., Expert, Master).
- **Contest Notifications**: Alerts the server about upcoming Codeforces, AtCoder, and CodeChef contests.
- **Background Updates**: Refreshes roles every 6 hours and checks for contests every 5 minutes.

## Setup

1.  **Install Dependencies**:
    The bot requires Python 3 and some libraries.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    Create a `.env` file in the root directory with your Discord Token:
    ```env
    DISCORD_TOKEN=your_discord_bot_token_here
    ```
    *(Note: This is already set up on your local machine)*

3.  **Permissions**:
    - Ensure the bot has `Manage Roles` permission.
    - Ensure the bot's role is **higher** than the rating roles (Newbie, Pupil, etc.) in the Discord Server Settings.
    - Create the rating roles in your server matching Codeforces ranks (newbie, pupil, specialist, expert, etc.).

## Usage

### Running the Bot

You can run the bot using the helper script:

```bash
./run_bot.sh
```

Or manually:

```bash
python3 cf_bot.py
```

### Commands

- **`!cf <handle>`**
  Links your Discord user to the specified Codeforces handle and updates your role.
  *Example:* `!cf tourist`

- **`!ping`**
  Checks if the bot is online.
  *Response:* `pong`

## Deployment

The bot is designed to run locally or on a server. Ensure the process stays alive (e.g., using `screen`, `tmux`, or a system service like `systemd` or `launchd`).
