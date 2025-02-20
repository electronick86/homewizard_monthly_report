import os
import requests
import smtplib
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

Base = declarative_base()
#engine = create_engine('sqlite:///database.db')
engine = create_engine('sqlite:///data/database.db')
Session = sessionmaker(bind=engine)
session = Session()

class EnergyReading(Base):
    __tablename__ = 'energy_readings'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_power_import_kwh = Column(Float, nullable=False)

Base.metadata.create_all(engine)

def fetch_energy_data():
    try:
        ip_address = os.getenv('HOMEWIZARD_IP')
        response = requests.get(f"http://{ip_address}/api/v1/data")
        response.raise_for_status()
        data = response.json()

        total_power_import_kwh = data.get("total_power_import_kwh")
        new_reading = EnergyReading(total_power_import_kwh=total_power_import_kwh)
        session.add(new_reading)
        session.commit()

        print(f"Data stored successfully: {total_power_import_kwh} kWh")

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")




def send_monthly_report():
    current_month = datetime.now().month
    current_year = datetime.now().year

    first_day_current_month = session.query(EnergyReading).filter(
        extract('month', EnergyReading.timestamp) == current_month,
        extract('year', EnergyReading.timestamp) == current_year
    ).order_by(EnergyReading.timestamp.asc()).first()

    previous_month = current_month - 1 if current_month > 1 else 12
    previous_month_year = current_year if current_month > 1 else current_year - 1

    first_day_previous_month = session.query(EnergyReading).filter(
        extract('month', EnergyReading.timestamp) == previous_month,
        extract('year', EnergyReading.timestamp) == previous_month_year
    ).order_by(EnergyReading.timestamp.asc()).first()

    if first_day_current_month and first_day_previous_month:
        consumption = first_day_current_month.total_power_import_kwh - first_day_previous_month.total_power_import_kwh

        # Obtenir le nom du mois pour le rapport (par exemple, "January")
        month_name = datetime(previous_month_year, previous_month, 1).strftime("%B %Y")

        # Formatter les dates sans les secondes
        previous_measure_date = first_day_previous_month.timestamp.strftime("%Y-%m-%d %H:%M")
        current_measure_date = first_day_current_month.timestamp.strftime("%Y-%m-%d %H:%M")

        msg = EmailMessage()
        msg['Subject'] = f'Monthly Energy Report for {month_name}: {consumption:.2f} kWh'
        from_name = os.getenv('SMTP_FROM_NAME')
        msg['From'] = f"{from_name} <{os.getenv('SMTP_FROM_EMAIL')}>"
        msg['To'] = os.getenv('REPORT_RECIPIENT_EMAIL')

        measurement_device_description = os.getenv('HOMEWIZARD_DESCRIPTION')
        measurement_device_ip = os.getenv('HOMEWIZARD_IP')

        measurements = session.query(EnergyReading).filter(
                EnergyReading.timestamp >= first_day_previous_month.timestamp,
                EnergyReading.timestamp < first_day_current_month.timestamp
            ).order_by(EnergyReading.timestamp.asc()).all()

        measurement_details = "\n".join(
                    f" - {measurement.timestamp.strftime('%Y-%m-%d %H:%M')}: {measurement.total_power_import_kwh} kWh"
                    for measurement in measurements
                )

        report_generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        msg.set_content(f"""
Monthly Energy Report
---------------------

Measurement device:
{measurement_device_description} ({measurement_device_ip})

{previous_measure_date}: {first_day_previous_month.total_power_import_kwh} kWh
{current_measure_date}: {first_day_current_month.total_power_import_kwh} kWh

Total consumption for {month_name}: {consumption:.2f} kWh


Detailed Measurements:
----------------------
{measurement_details}

Report generated at: {report_generated_at}
        """)

        try:
            with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
                server.starttls()
                server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
                server.send_message(msg)
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")

    else:
        print("Not enough data to send a report.")