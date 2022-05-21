# stock_bot
A Telegram chat bot for getting news about the US stock market

### Deployment guide
To run this app for local development you have to provide right values for environment variables specified in '.env'
and install required python packages specified in 'requirements.txt'. You can find both files in root directory of project.

**Warning:** Remember to place values that have white space inside them between **""**

For preventing git merge conflicts in **.env** file after updating it; run following command:

```shell
git update-index --assume-unchanged .env
```
To start a HTTP tunnel forwarding to your local machine and setting a webhook to connect to telegram 
you can use [ngrok](https://ngrok.com/). Update `.env` file and set `SERVER_URL` variable with the forwarding address which ngrok give you.