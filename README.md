# How to deploy to EC2


1) Create a new .env based on your credentials
2) Scp to .env to client
`scp -i <.pem file> <.env location> <user>@<host>:~/mintToText/app/`

3) SSH into client
`ssh -i <.pem file> <user>@<host>`

```
git clone https://github.com/grantjayy/mintToText.git
cd mintToText
chmod +x ./newInstance.sh
./newInstance
```