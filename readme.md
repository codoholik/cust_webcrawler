# Steps to run the application:

- Clone the repo on desktop using below command in Terminal

      git clone git@github.com:codoholik/cust_webcrawler.git

- Change directory to cloned folder

      cd cust_webcrawler

- Create virtual environtment

      python3 -m venv venv

- Activate the environment

      source venv/bin/activate (for linux)
      venv\Scripts\activate (for windows)

- Install requirements

      pip install -r requirements.txt

- create a .txt file consisting of domains with each domain on the new line.

- start the crawler

      python crawler.py <domains_file_path> <comma_sep_patterns>

- At last you will have a `output.txt` in same dir as crawler.py exists.
