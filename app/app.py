import os
import logging
import mintapi
import pendulum
from flask import Flask, request
from time import sleep
from twilio.rest import Client
from dotenv import load_dotenv

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

load_dotenv()

BUDGET_AMOUNT = int(os.getenv("BUDGET"))


def send_msg(text):
    client = Client(os.getenv("TWILIO_ACC"), os.getenv("TWILIO_TOKEN"))
    client.messages.create(to=os.getenv("CLIENT_PHONE"), from_=os.getenv("APP_PHONE"), body=text)


def send_xml(text):
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>{text}</Body></Message></Response>'


def input_callback(arg):
    logger.info("MFA Callback")

    # sleeps for 30 seconds
    sleep(30)

    # Get code from txt file
    with open("/tmp/mfa.txt", "r") as f:
        code = f.read()
        logger.debug(f"MFA Code {code}")
        return code


def main():
    output = {}

    logger.debug("Logging into Mint...")
    mint = mintapi.Mint(  # Initialize Mint API For scraping
        os.getenv("MINT_USER"),
        os.getenv("MINT_PASS"),
        headless=True,
        mfa_input_callback=input_callback,
        use_chromedriver_on_path=True,
        mfa_method="sms",
    )

    logger.debug("Initiating Account Refresh")
    mint.initiate_account_refresh()

    for acc in mint.get_accounts():
        if os.getenv("DEBIT_ACC") in acc["accountName"]:
            output["debit"] = acc["currentBalance"]

        if os.getenv("CREDIT_CARD") in acc["accountName"]:
            output["credit"] = acc["value"]

    # Get Transactions and close Mint API
    now = pendulum.now(tz="America/Los_Angeles")
    df = mint.get_transactions(
        start_date=now.start_of("month").format("MM/DD/YY"), end_date=now.end_of("month").format("MM/DD/YY")
    )
    mint.close()

    ignore = ["income", "transfer", "credit card payment"]  # Categories of mint to ignore
    output["spent"] = df[(~df["category"].isin(ignore)) & (df.transaction_type != "credit")].sum()[
        "amount"
    ]  # Sum dataframe of all debit transactions without unwanted categories

    period = now.end_of("month") - now

    # Values for return Message
    output["month"] = now.format("MMMM")
    output["remainder"] = BUDGET_AMOUNT - float(output["spent"])
    output["daily"] = output["remainder"] / period.days
    output["weekly"] = output["remainder"] / period.weeks
    output["budget"] = BUDGET_AMOUNT

    # Send Message with Twilio
    message = (
        "Left to spend for {month}: ${remainder:,.2f}\n"
        "Total spent for {month}: ${spent:,.2f}\n\n"
        "You can spend ${daily:,.2f} each day, or ${weekly:,.2f} each week to stay on budget.\n\n"
        "Debit Account Balance: ${debit:,.2f}\n"
        "Credit Card Balance: ${credit:,.2f}\n"
        "Monthly Budget: ${budget:,.2f}"
    ).format(**output)

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
            logger.debug(f"Saved MFA Code as {body['Body']}")
            return "Done"
    except Exception as e:
        send_msg(f"Failed. Error was -->\n\n{e}")

    return "Done"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Production
    # app.run(port=9000)  # Debug
