import sys
import angellist
import json
import numpy as np
import re
#TODO: different class different file?
# param fp is a string for json file we wish to open
# returns result of json.load(fp), type dict
def load_json(fp) :
  with open(fp) as df :
    return json.load(df)

def write_json(fp, data):
  with open(fp, 'w') as outfile:
    json.dump(data, outfile)

class LobJsonMake(object) :
  def __init__(self) :
    self.fps = ['json/jobtag.json', 'json/job2.json', 'json/job3.json', 'json/job4.json', 'json/job5.json', 'json/job6.json']
    #param data is dict from filter_companies with information we will add to json/skills.json
  #returns dict that counts occurences of skills
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

  #param data is a dict from api call getJobsByTag
  #get id's and skill information of each company
  #returns a dict of each company's id and its name 
  def filterCompanies(self, data):
    comp_data = {}
    startup = data["jobs"] #array of startup objects
    for e in startup:
      comp = e["startup"]
      if comp["name"] not in comp_data:
        comp_data[comp["name"]] = (comp["id"], e["tags"])
    #TODO: i need all the companies from all my json files so I can do classification
    return comp_data

  # compile all the information from 6 pages of api call to json/skills.json
  def allSkills(self) :
    for p in self.fps :
      comp_data = self.filterCompanies(load_json(p))
      self.countSkills(comp_data)

  # compile all the information from 6 pages of api call to json/skills.json
  # ended up with 73 companies
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

    #prepares company info
  #TODO: make skills comma-separated values
  def vectorCompDict(self, cand, al) :
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
    #TODO: If i want to do comma separated values, I should transform the cand dict first
    self.map = {"mobile": 0, "skills": 1, "db": 2, "location": 3, "language": 4}
    self.comp_vecs = vectorize(cand)
    self.cand_vec = np.array([1 for i in range(0, len(self.map))])

  # just add job values 
  def simpleRank(self) :
    pass

  def normalize(self, v):
    norm=np.linalg.norm(v)
    if norm==0: 
       return v
    return v/norm

  def cosineSimilarity(self) :
    for c_id , vec in self.comp_vecs.iteritems() :
      np_vec = np.array(vec)
    pass

  #param cand is dict from candidate's json file
  #TODO: need a function to take car of the comma-separated values
  #preparation for cosine similarity
  def vectorize(self) :
    cand = self.cand
    comp_jobs = load_json('json/comp_vec_dict.json')
    comp_vecs = {}
    for c_id, info in comp_jobs.iteritems() :
      comp_vec = [0 for i in range(0, len(self.map))]
      for sk, count in info.iteritems() :
        for k, v in cand.iteritems() :
          if re.findall(v, str(sk)) :
            comp_vec[self.map[k]] = count
      comp_vecs[str(c_id)] = comp_vec
    #tODO: send this info out
    print comp_vecs 

class Lob(object) :
  #wrapper class for the bulk of our work #modularize

#TODO: validation, separate class? 
#TODO: separate ranking class?

  def __init__(self, token) :
    self.access_token = token
    self.candidate_keys = ["language", "location", "db", "mobile", "skills"]
    #TODO: json field?

  #TODO: get json file path for candidate attributes from command line
  def getInput(self, vec):
    ready = False
    res = (ready, {})
    #loop til we open json file with no error
    while (not ready) :
      response = raw_input("Please submit the path to your candidate json file : ")
      data = load_json(response)[0]
      res = self.checkCand(data)
      ready = res[0]
    vectorize(vec, data)

  #data is a dict of candidate's json file
  #makes sure the data conforms to our requirements
  #while not make requirement, ask for input (getInput)
  # if we meet requirements, we will be able to proceed with a True boolean
  def checkCand(self, data) :
    for e in self.candidate_keys :
      if e not in data :
        print "Your json file did not meet our requirements, you are missing a %s field" % (e) 

    return (True, data)

  #param vec is of class LobVectorize
  #data is candidate profile dict
  #call this function when you pass checkCand
  def vectorize(self, vec, data) :
    vec.vectorize(data)


  # param al is an AngelList() object
  def getJobByTag(self, al, tag_id = None, page = None) :
    job = al.getJobByTag(al.access_token, tag_id, 2)
    return job
    
if __name__ == '__main__':
  #TODO: use a db to hide credentials?
  #i might just hash it

  al = angellist.AngelList()
  al.client_id = 'fe4a1fb11ab1a4e0a9595b9c31e7f366af494f1bc0de05e7'
  al.access_token = '94ece8695020668b807e8b19d2028be7f1a7bbe43546f9dd'
  al.client_secret = '3021d52bd5941d2de685c96a03ce056f0b002dcd9ffff9c2'
  # auth_url = al.getAuthorizeURL()

  lobsta = Lob(al.access_token)
  # job = lobsta.getJobByTag(al, '14766', 6)
  # print json.dumps(al.getStartups(al.access_token, 6702))
  jsonmake = LobJsonMake()
  # jsonmake.allJobsSkills()
  cand = load_json('cand1.json')
  # print (cand)
  # jsonmake.vectorCompDict(cand, al)
  lobvec = LobVectorize(cand)
  # with open('json/job6.json', 'w') as out:
  #   json.dump(job, out)
  # lobsta.getInput(v)


