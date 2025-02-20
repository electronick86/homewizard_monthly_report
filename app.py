from flask import Flask
from fetch_energy import fetch_energy_data, send_monthly_report
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

def schedule_fetch():
    scheduler = BackgroundScheduler(daemon=True)
    # Configurer le déclencheur cron pour exécuter la tâche tous les jours à 8h00
    scheduler.add_job(fetch_energy_data, 'cron', hour=2, minute=0)
    scheduler.add_job(send_monthly_report, 'cron', day=1, hour=8, minute=0)

    scheduler.start()

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

    app.run(host='0.0.0.0', port=5000)