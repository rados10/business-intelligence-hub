import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import slack_sdk
import json

class SalesAnalyzer:
    def __init__(self, db_path, slack_token):
        self.db_path = db_path
        self.slack_client = slack_sdk.WebClient(token=slack_token)
    
    def get_daily_metrics(self):
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT 
            DATE(transaction_date) as date,
            COUNT(*) as total_transactions,
            SUM(quantity * price) as total_revenue,
            COUNT(DISTINCT customer_id) as unique_customers,
            AVG(quantity * price) as avg_transaction_value
        FROM sales
        WHERE transaction_date >= DATE('now', '-7 days')
        GROUP BY DATE(transaction_date)
        ORDER BY date DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def analyze_trends(self):
        metrics = self.get_daily_metrics()
        
        # Calculate week-over-week growth
        current_revenue = metrics.iloc[0]['total_revenue']
        last_week_revenue = metrics.iloc[-1]['total_revenue']
        growth = ((current_revenue - last_week_revenue) / last_week_revenue) * 100
        
        return {
            "current_day_revenue": current_revenue,
            "weekly_growth": growth,
            "unique_customers_today": metrics.iloc[0]['unique_customers'],
            "avg_transaction_value": metrics.iloc[0]['avg_transaction_value']
        }
    
    def send_slack_alert(self, channel_id, metrics):
        message = f"""
📊 *Daily Sales Report*
Revenue: ${metrics['current_day_revenue']:,.2f}
Weekly Growth: {metrics['weekly_growth']:,.1f}%
Unique Customers: {metrics['unique_customers_today']}
Avg Transaction: ${metrics['avg_transaction_value']:,.2f}
        """
        
        self.slack_client.chat_postMessage(
            channel=channel_id,
            text=message,
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": message}
                }
            ]
        )

if __name__ == "__main__":
    analyzer = SalesAnalyzer("sales.db", "YOUR_SLACK_TOKEN")
    metrics = analyzer.analyze_trends()
    analyzer.send_slack_alert("YOUR_CHANNEL_ID", metrics)