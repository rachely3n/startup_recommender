#README

## Running
To run the program, simply type the following in your terminal:
`python lob.py` 

You will then be prompted to submit a path to a valid candidate json file. The json file is in the following format :

`{"mobile": "iOS", "skills": "Ruby on rails", "db": "Mongodb", "location": "San Francisco", "language": "Scala"}`

You can type cand1.json to run my supplied candidate json profile

### requirements:
numpy and scipy
### other libraries:
I used a library for querying the AngelList API (angellist.py) from https://github.com/Falicon/AngelList; however, I had to add my own function to get the information I wanted.
### API credentials 
They are not hidden for this program. Ideally, I would store them encoded in a database. 
### Output
They are printed in command line. They are ranked in order of descending score (highest score is highest match). 

Provided are the company name, product description, and company size. These were chosen because it gives a nice and brief overview of the startup. 
## Data and Design
For the data, I've decided not to query each time because these are considerably big json files to save time. Ideally, I would query since jobs are posted everyday. 

I really only needed to query the API for software engineering jobs for each startup because I filtered information I needed based on that one json file. 
### Json files from AngelList's API
Not all json files that I've generated were used in classification and ranking of the recommendations

`lobsta.getJobByTag(LobJsonMake(), al)` (where lobsta is an instance of the class Lob) generates the files `['json/jobtag.json', 'json/job2.json', 'json/job3.json', 'json/job4.json', 
    'json/job5.json', 'json/job6.json'] `
    
 Those files are used by `allJobsSkills`, which lists for each company the number of times the skill/tag was mentioned in jobs under that company. `allJobsSkills` then yields `jobs_skills_count.json`
 
 
 `vectorCompDict(cand)` uses `jobs_skills_count.json` to prepare information about each company that matches attributes in the candidate's profile. The method then writes information to `json/comp_vec_dict.json`, will be used by the LobVectorize class.

## Design
I've limited the tag_id when I first call getJobByTag to software engineering because I wanted to focus the skillset of software engineers. This is because I understand more about what software engineers know, which helps me design my program versus also including roles like management and whatnot. 
### Classification
The classification is very simple right now. The score is made of two parts: The norm of the vector and the cosine similarity of the company's vectors to the candidate's vectors.

#### Candidate profile
For each key in the json file, we have a weight of 1 in the vector.
#### Vectorizing
In `vectorize(cand)`, we loop through each company's data from `comp_vec_dict.json` to see if any of the skills in the company match the ones the candidate provided. 

We then add the value from the datum if it's a match. This value is the number of jobs the company offers that ask for that skill. 

Furthermore, we match based on a regex. If the skill the user provided can be found anywhere in the datum string, it could be a match, such as ruby and ruby on rails. We would probably want these two skills to match. What is ruby without rails?  
#### Measurement and Score
Given the limited candidate profile, many of the cosine similarities were the same, so I would include the norm of the vector as well for a very simple way to generate a similarity score. The more jobs that the company offers that matches skills in the candidate, the likelier the user might want to apply. 
