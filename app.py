from flask import Flask
from fetch_energy import fetch_energy_data, send_monthly_report
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def schedule_fetch():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_energy_data, 'cron', hour=2, minute=0)
    #scheduler.add_job(fetch_energy_data, 'cron', minute='*/1')
    scheduler.add_job(send_monthly_report, 'cron', day=1, hour=8, minute=0)
    scheduler.start()
    logging.info("Scheduler started.")

@app.route('/')
def index():
    return "Hello, this is your HomeWizard energy service."

@app.route('/send-report')
def test_send_report():
    send_monthly_report()
    return "Monthly report sent."

@app.route('/fetch-data')
def test_fetch_data():
    fetch_energy_data()
    return "Data fetched."

if __name__ == "__main__":
    # Lancer le fetch initial et initialiser le scheduler
    schedule_fetch()
    logger.info("Application started.")
    app.run(host='0.0.0.0', port=5000)