# ACME Settlement Service - Tyler Neath

## Problem

The goal is to process settlement values based on date for different merchants available from the ACME Payments API. The biggest drawback we have is that the API is consistently unreliable and returns inconsistent error codes. 

## Solution 

The solution implemented as a workaround was to leverage the usage of a 'retry' mechanism in cases where we receive inconsistent responses. For the time being, we rety calls to the ACME API for 3 times with a fixed wait period of around 2 seconds. However, this can be adjusted if needed (eg. implementing exponential backoff, more retries, random timescales etc). 

Since the status codes are inconsistent, we rely on the message details to know wether we have made an erroneous request or not. For example in the case of retrieving invalid merchants that do not exist, we rely on the message detail rather than the code. 

## Endpoint 
`POST /settlement`
merchant_id (string): The merchant id requested.
transactions_date (string): The date for which to retrieve transactions, in the format YYYY-MM-DD.


## Getting Started
```bash
git clone https://github.com/YOUR_USERNAME/acme-settlement-service.git
cd acme-settlement-service
```

(Optional) Set up a virtual envrionment 
```bash
python3 -m venv venv
source venv/bin/activate
```
install dependencies 

```bash
pip install -r requirements.txt
```

run the service 
```bash
uvicorn main:app --reload
```
the api will run on ``localhost:8000``


### Future Improvements
A potential follow-up improvement would be to leverage asynchronous processing to calculate the settlement for a merchant that has a large number of transactions. This would allow the service to handle multiple settlement calculations concurrently, improving performance and scalability. I believe this would be most helpful for merchants with high transaction volumes, where processing time could become a bottleneck.