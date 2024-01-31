# README #


**Python version:** 3.6.8
`generate_tags.py`
tag audio tracks located in a given folder and save tags in .json format for each track.

`tags_to_csv.py`
check all tag .json files located in a given folder and write the tags to a single CSV file.

`constants.py`
update the values of 'KEY' and 'BASE_URL' with your Musiio API Key and API Url.


### Setup Environment & Install Dependencies


```
git clone https://github.com/Musiio-AI/tagging_tool.git

cd project root folder

pip install virtualenv

virtualenv env

.\env\Scripts\activate

pip install -r .\requirements.txt
```


### Update constants.py with API Key

```python
KEY = "Replace With Your Musiio API KEY"
```

### Tag Generation and generate the CSV

```bash
python main.py --source-path ./test_files/ --json-destination-path ./json --csv-destination-path ./csv
```


### Use config.json file
```
{
  "tagging_api": "PRODUCTION" / "TEST,
  "log_level": "INFO" / "DEBUG",
  "n_processes": "5",
  "tags": "['CONTENT TYPE','HIT POTENTIAL','GENRE V3','GENRE B2KBK7Q822','MOOD','BPM','ENERGY','KEY SHARP','INSTRUMENTATION']"
}
```
