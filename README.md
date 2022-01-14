# Mint Transactions to Text

Do you use Mint.com primarily for tracking your expenses? Do you want to have an (almost) automated message sent to you each day about how much left you have left to spend overall, given a budget?

Look no further. This app does all of this.

Each morning, send a text message to a application number that you have with Twilio, Mint will send you an MFA code, then you send that number back to the application number. You will then recieve a message with your spending limits for the rest of the month.

Here is an example of the message you will recieve:

```
Left to spend for January: $152.31
Total spent for January: $2047.69

You can spend $8.02 each day, or $76.15 each week to stay on budget.
```

The process flow looks like this:
1) Send "Start" to the number you have registered with Twilio
2) Mint will send you a MFA Code, copy and send this code to the number you have registered with Twilio
3) The app will send you a text with the details of your spending for that month

## Requirements

You need to have an account with Twilio, and Mint

## Specifications

The app uses the unofficial Mint API to scrape data from the site. It gets all your transactions for the current month, then filters out the transaction categories (assigned in Mint) that you want ignore (default is: income, transfer, credit card payment).

The app is self hosted in a docker container, and uses dockerized NGINX to deploy.

Selenium is used to scrape the site, and Flask is used to handle requests.

The app needs to be hosted on a server. It cannot be hosted on AWS Lambda. I have not tried other serverless applications. A free EC2 instance works just fine, and there is minimal configuration since the `newInstance.sh` script does everything for you (on an Ubuntu server).

You will need to update the `.env.example` file. Remove the "example" from the end of the file name and add your Mint username and password, Twilio Application token and secret, and your personal phone number that you want to use with the app, and the application phone number that you use in Twilio.

You will also need to send a webhook to your server from within the Twilio console.
## Local Development

Run the app locally for development with the python command
```
cd app
python3 app.py
```

## Deployment

Run `docker-compose up` to run in a deployment environment
## How to deploy to EC2


1) Create a new .env based on your credentials
2) Scp the .env to client
`scp -i <.pem file> <.env location> <user>@<host>:~/mintToText/app/`

3) SSH into client
`ssh -i <.pem file> <user>@<host>`

```
git clone https://github.com/grantjayy/mintToText.git
cd mintToText
chmod +x ./newInstance.sh
./newInstance
```