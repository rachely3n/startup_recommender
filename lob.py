import sys
import angellist
import json
import operator
import numpy as np
import scipy.spatial.distance as sp
import re
#TODO: comments for each class 

# param fp is a string for json file we wish to open
# returns result of json.load(fp), type dict
def load_json(fp) :
  with open(fp) as df :
    return json.load(df)

# param fp is a string for json file we wish to write to
# writes dict data to fp in json format
def write_json(fp, data):
  with open(fp, 'w') as outfile:
    json.dump(data, outfile)

# given certain json files, filter out more data to make other needed json files
# not all json files created were used to rank, but some files 
# provided information that were useful in designing the system
class LobJsonMake(object) :

  def __init__(self) :
    self.fps = ['json/jobtag.json', 'json/job2.json', 'json/job3.json', 'json/job4.json', 
    'json/job5.json', 'json/job6.json']

  # param data is dict from filter_companies with information we will add to json/skills.json
  # writes dict to json that counts occurences of skills in jobs listed under each company
  def countSkills(self, data):
    sk_count = self.load_json('json/skills.json')
    for key, value in data.iteritems() :
      info = value[1] #non-id list
      # print info
      for tag in info : #skill is each object
        if tag["tag_type"] == "SkillTag" :
          if tag["name"] not in sk_count :
            sk_count[tag["name"]] = 1
          else :
            sk_count[tag["name"]] += 1
        else :
          continue
    write_json('json/skills.json', sk_count)

  # param data is a dict from api call getJobsByTag
  # get id's and skill information of each company
  # returns a dict of each company's id and its name 
  def filterCompanies(self, data):
    comp_data = {}
    startup = data["jobs"] #array of startup objects
    for e in startup:
      comp = e["startup"]
      if comp["name"] not in comp_data:
        comp_data[comp["name"]] = (comp["id"], e["tags"])
    return comp_data

  # param al is an AngelList() object
  # param tag_id is the id of the tag name
  # param page is page of response requested
  # returns dict of json output of API call getJobByTag (see angellist.py)
  # used 14766 for tag since it's software engineering jobs
  def getJobByTag(self, al, tag_id = 14766, page = None) :
    job = al.getJobByTag(al.access_token, tag_id, page)
    return json.dumps(job)
    
  # compile all the information from 6 pages of api call to json/skills.json
  def allSkills(self) :
    for p in self.fps :
      comp_data = self.filterCompanies(load_json(p))
      self.countSkills(comp_data)

  # compile all the information from 6 pages of api call to json/skills.json
  # lists all jobs for each company
  # ended up with 73 companies
  # writes to json/alljobs.json
  def allJobs(self) :
    all_jobs = {}
    for p in self.fps :
      data = load_json(p)
      info = data["jobs"] #info is an array that has all the jobs info 
      for comp in info : #comp is a dict with that startup's info and all jobs it's offering
        startup = comp["startup"]
        jobs = comp["tags"]
        c_id = startup["id"]
        name = startup["name"]
        #store comp
        if c_id not in all_jobs :
          all_jobs[c_id] = {"name" : name, "jobs" : comp["tags"]}
        else : #extend because companies seem to show up more than once..
          all_jobs[c_id]["jobs"].extend(jobs)
    write_json('json/alljobs.json', all_jobs)

  # compile all the information from 6 pages of api call to json/skills.json
  # company: {skill}
  # writes to json/jobs_skills_count.json
  def allJobsSkills(self) :
    all_jobs = {}
    for p in self.fps :
      data = load_json(p)
      info = data["jobs"] #info is an array that has all the jobs info 
      for comp in info : #comp is a dict with that startup's info and all jobs it's offering
        startup = comp["startup"]
        jobs = comp["tags"]
        c_id = startup["id"]
        name = startup["name"]
        for job in jobs :
          if c_id not in all_jobs :
            all_jobs[c_id] = {job["name"] : 1}
          else :
            if job["name"] not in all_jobs[c_id] :
              all_jobs[c_id][job["name"]] = 1
            else :
              all_jobs[c_id][job["name"]] += 1
    write_json('json/jobs_skills_count.json', all_jobs)

  # param cand is dict with candidate information
  # prepares information about each company that matches things in
  # candidate's profile
  # writes information to json/comp_vec_dict.json, will be used by LobVectorize class
  def vectorCompDict(self, cand) :
    comp_jobs = load_json('json/jobs_skills_count.json')
    vec_info = {}
    for k, v in cand.iteritems() :
      for c_id, info in comp_jobs.iteritems() :
        for sk, count in info.iteritems() :
          if re.findall(v, sk) : #design decision, since what we typed might not be all of the skill name
            if c_id not in vec_info :
              vec_info[c_id] = {v : count}
            else :
              vec_info[c_id][sk] = count
    write_json('json/comp_vec_dict.json', vec_info)

class LobVectorize(object) :

  def __init__(self, cand) :
    self.map = {"mobile": 0, "skills": 1, "db": 2, "location": 3, "language": 4}
    self.cand = cand
    self.comp_vecs = self.vectorize()
    self.cand_vec = self.normalize(np.array([1 for i in range(0, len(self.map))]))

  # normalizes a vector v
  def normalize(self, v):
    norm=np.linalg.norm(v)
    if norm==0: 
       return v
    return v/norm

  # just add job values for each company vector by using norm
  # returns a dict, c_id : score
  def simpleRank(self) :
    scores = {}
    for c_id , vec in self.comp_vecs.iteritems() :
      scores[c_id] = np.linalg.norm(vec)
    return scores

  # adds scores from cosineSimilarity() and simpleRank() for each company
  # returns a dict, c_id : score
  def calcScores(self):
    cos = self.cosineSimilarity()
    norm = self.simpleRank()
    scores = {}
    for k in self.comp_vecs.iterkeys() :
      scores[k] = norm[k] + cos[k]
    return scores

  # sorts the dictionary of c_id to scores output by cosineSimilarity()
  def rank(self):
    scores = self.calcScores()
    #TODO: rank and write a function to format company info
    sorted_x = sorted(scores.items(), reverse = True, key=operator.itemgetter(1))
    return sorted_x

  # print the companies that best fit the candidate json
  def companies(self, al) :
    companies = self.rank()
    n = min(10, len(companies)) #limit to 10 startups
    i = 1
    for datum in companies[:n] :
      c_id = datum[0]
      c_info = al.getStartups(startup_id = c_id)
      print 'Startup %s: %s \nProduct Description:\n%s \nCompany size: %s\n' % (i,
       c_info["name"], c_info["product_desc"], c_info["company_size"])
      i += 1

  # calculates the cosine similarity for each company between each company's
  # vector and the candidate vector
  # returns a dict of company id to their score
  def cosineSimilarity(self) :
    scores = {}
    for c_id , vec in self.comp_vecs.iteritems() :
      np_vec = self.normalize(np.array(vec))
      mat = [np_vec, self.cand_vec]
      score = sp.cdist(mat, mat, 'cosine')
      scores[c_id] = score[0][1]
    return scores 

  # param cand is dict from candidate's json file
  # preparation for cosine similarity
  # if no matches at all, prints no matches
  def vectorize(self) :
    cand = self.cand
    comp_jobs = load_json('json/comp_vec_dict.json')
    comp_vecs = {}
    blank = True
    for c_id, info in comp_jobs.iteritems() :
      comp_vec = [0 for i in range(0, len(self.map))]
      for sk, count in info.iteritems() :
        for k, v in cand.iteritems() :
          if re.findall(v.lower(), str(sk)) :
            blank = False
            comp_vec[self.map[k]] = count
      comp_vecs[str(c_id)] = comp_vec
    if blank :
      print "no matches found"
      sys.exit()
    else :
      return comp_vecs

class Lob(object) :
  # wrapper class for the bulk of the work
  # wrapper methods
  # given a json file for a candidate with the following attributes: 
  # "language", "location", "db", "mobile", "skills"
  # recommend 10 companies for the candidate to apply to
  def __init__(self, token) :
    self.access_token = token
    self.candidate_keys = ["language", "location", "db", "mobile", "skills"]

  # asks for input from user for json file of candidate information
  # checks it's in a valid .json format
  # loads json file, starts the ranking process
  def getInput(self):
    ready = False
    res = (ready, {})
    #loop til we open json file with no error
    while (not ready) :
      response = raw_input("Please submit the path to your candidate json file : ")
      if not re.findall('^\w+.json$', response):
        print "Please submit a proper .json file path (ex. data.json)"
        continue
      cand = load_json(response)
      res = self.checkCand(cand)
      ready = res[0]
    
    self.getStartups(cand)

  #data is a dict of candidate's json file
  #makes sure the data conforms to our requirements
  #while not make requirement, ask for input (getInput)
  # if we meet requirements, we will be able to proceed with a True boolean
  def checkCand(self, data) :
    for e in self.candidate_keys :
      if e not in data :
        print "Your json file did not meet our requirements, you are missing a %s field" % (e) 

    return (True, data)

  #param cand is the dict containing the candidate's information
  #call's the methods in class LobVectorize to get companies
  def getStartups(self,cand) :
      lobvec = LobVectorize(cand)
      lobvec.companies(al)

  # param js is a LobJsonMake() object
  # param al is an AngelList() object
  # param tag_id is the id of the tag name
  # param page is page of response requested
  # returns dict of json output of API call getJobByTag (see angellist.py)
  # used 14766 for tag since it's software engineering jobs
  def getJobByTag(self, js, al, tag_id = 14766, page = None) :
    return js.getJobByTag(al, tag_id, page);
    
if __name__ == '__main__':

  al = angellist.AngelList()
  al.client_id = 'fe4a1fb11ab1a4e0a9595b9c31e7f366af494f1bc0de05e7'
  al.access_token = '94ece8695020668b807e8b19d2028be7f1a7bbe43546f9dd'
  al.client_secret = '3021d52bd5941d2de685c96a03ce056f0b002dcd9ffff9c2'

  lobsta = Lob(al.access_token)
  lobsta.getInput()

