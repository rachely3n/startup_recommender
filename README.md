#README

## Running
To run the program, simply type 
`python lob.py` 

You will then be prompted to submit a path to a valid candidate json file. The file is in the following format :

`{"mobile": "iOS", "skills": "Ruby on rails", "db": "Mongodb", "location": "San Francisco", "language": "Scala"}`

### requirements:
numpy and scipy
### other libraries:
I used a library for querying the AngelList API; however, I had to add my own function to get the information I wanted.
## Data and Design
### Json files from AngelList's API
Not all json files that I've generated were used in classification and ranking of the recommendations
`allJobsSkills()`