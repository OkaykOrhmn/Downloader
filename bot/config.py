class BotConfig:
    def __init__(self, admin_ids, welcome_message, webhook_url, webhook_port) -> None:
        self.admin_ids = admin_ids
        self.welcome_message = welcome_message
        self.webhook_url = webhook_url
        self.webhook_port = webhook_port