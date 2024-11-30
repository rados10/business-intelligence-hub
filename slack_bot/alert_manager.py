import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class AlertManager:
    def __init__(self, slack_token):
        self.client = WebClient(token=slack_token)
        self.default_channel = "#sales-alerts"
    
    def send_metric_alert(self, metric_name, current_value, threshold, comparison="above"):
        """
        Sends an alert when a metric crosses a threshold
        """
        emoji = "🔴" if comparison == "above" else "🟡"
        message = (
            f"{emoji} *Metric Alert*\n"
            f"*{metric_name}* has crossed the {comparison} threshold\n"
            f"Current value: {current_value}\n"
            f"Threshold: {threshold}"
        )
        
        try:
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message,
                blocks=[
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message}
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"<!date^{int(time.time())}^Alert triggered at {{date_num}} {{time_secs}}|{time.ctime()}>"
                            }
                        ]
                    }
                ]
            )
            return response
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            return None
    
    def send_daily_report(self, metrics):
        """
        Sends a formatted daily report to Slack
        """
        report = (
            "📊 *Daily Sales Report*\n\n"
            f"*Revenue*: ${metrics['revenue']:,.2f}\n"
            f"*Orders*: {metrics['orders']}\n"
            f"*Average Order Value*: ${metrics['aov']:,.2f}\n"
            f"*Active Customers*: {metrics['active_customers']}\n\n"
            "*Top Products*:\n"
        )
        
        for product in metrics['top_products']:
            report += f"• {product['name']}: ${product['revenue']:,.2f}\n"
        
        try:
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=report,
                blocks=[
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": report}
                    }
                ]
            )
            return response
        except SlackApiError as e:
            print(f"Error sending report: {e.response['error']}")
            return None

    def create_incident(self, severity, description):
        """
        Creates an incident thread for tracking issues
        """
        severity_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        
        message = (
            f"{severity_emoji.get(severity, '⚪')} *New Incident*\n"
            f"*Severity*: {severity.upper()}\n"
            f"*Description*: {description}\n"
            "Please reply to this thread with updates."
        )
        
        try:
            # Create the initial incident message
            response = self.client.chat_postMessage(
                channel=self.default_channel,
                text=message
            )
            
            # Start a thread with additional information
            self.client.chat_postMessage(
                channel=self.default_channel,
                thread_ts=response['ts'],
                text="🔍 *Incident Timeline*\n• Incident created and tracking started"
            )
            
            return response
        except SlackApiError as e:
            print(f"Error creating incident: {e.response['error']}")
            return None