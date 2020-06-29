# Route53 dump

Loops through all Route53 zones in an AWS accounts and exports the A and CNAME records to YAML files.

```
export s3_bucket=OUTPUT-BUCKET-NAME
cd src
pip install -r requirements.txt
python main.py
```
