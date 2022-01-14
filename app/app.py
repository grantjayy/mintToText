import os
import logging
import mintapi
import pendulum
from flask import Flask, request
from time import sleep
from twilio.rest import Client
from dotenv import load_dotenv

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

load_dotenv()

BUDGET_AMOUNT = int(os.getenv("BUDGET"))


def send_msg(text):
    client = Client(os.getenv("TWILIO_ACC"), os.getenv("TWILIO_TOKEN"))
    client.messages.create(to=os.getenv("CLIENT_PHONE"), from_=os.getenv("APP_PHONE"), body=text)


def send_xml(text):
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>{text}</Body></Message></Response>'


def input_callback(arg):
    logger.debug("callback")

    # sleeps for 25 seconds
    sleep(20)

    # Get code from txt file
    with open("/tmp/mfa.txt", "r") as f:
        code = f.read()
        logger.debug(f"MFA Code {code}")
        return code


def main():
    logger.debug("Logging into Mint...")

    mint = mintapi.Mint(  # Initialize Mint API For scraping
        os.getenv("MINT_USER"),
        os.getenv("MINT_PASS"),
        headless=True,
        mfa_method="sms",
    )

    logger.debug("Initiating Account Refresh")
    mint.initiate_account_refresh()

    # Get Transactions and close Mint API
    now = pendulum.now(tz="America/Los_Angeles")
    df = mint.get_transactions(
        start_date=now.start_of("month").format("MM/DD/YY"), end_date=now.end_of("month").format("MM/DD/YY")
    )
    mint.close()

    ignore = ["income", "transfer", "credit card payment"]  # Categories of mint to ignore
    spent = df[(~df["category"].isin(ignore)) & (df.transaction_type != "credit")].sum()[
        "amount"
    ]  # Sum dataframe of all debit transactions without unwanted categories

    # Values for return Message
    month = now.format("MMMM")
    period = now.end_of("month") - now
    days_left = period.days
    weeks_left = period.weeks
    remainder = BUDGET_AMOUNT - spent

    # Send Message with Twilio
    message = f"Left to spend for {month}: ${round(remainder,2)}\nTotal spent for {month}: ${round(spent,2)}\n\nYou can spend ${round((remainder/days_left), 2)} each day, or ${round((remainder/weeks_left),2)} each week to stay on budget."
    send_msg(message)


@app.route("/", methods=["POST"])
def handler():
    try:
        body = request.form.to_dict()

        if not os.getenv("CLIENT_PHONE") in body["From"]:  # Check if phone is known
            return send_xml("Not a known phone")

        if "Start" in body["Body"]:  # Start Main sequence
            send_msg("Starting... You should receive a MFA Code from Mint shortly.")
            try:
                main()
            except Exception as e:
                send_msg(f"Failed. Error was -->\n\n{e}")
            return "Done"

        if body["Body"].isnumeric():  # Check for the MFA Code
            with open("/tmp/mfa.txt", "w") as f:  # Write to file for use soon
                f.write(body["Body"])
            return "Done"
    except Exception as e:
        send_msg(f"Failed. Error was -->\n\n{e}")


    return "Done"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Production
    # app.run(port=9000)  # Debug
