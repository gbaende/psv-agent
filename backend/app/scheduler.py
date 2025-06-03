from apscheduler.schedulers.background import BackgroundScheduler

def send_slack_checkin():
    # Placeholder for Slack DM logic
    print("Sending scheduled Slack check-in...")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Monday, Wednesday, Friday at 9am
    scheduler.add_job(send_slack_checkin, 'cron', day_of_week='mon,wed,fri', hour=9, minute=0)
    scheduler.start() 