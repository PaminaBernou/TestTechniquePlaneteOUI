# -*- coding: utf-8 -*-
"""
Test technique pour Planète OUI
Par Pamina Bernou
"""

import requests
import operator
import json
import sys

fromDate = sys.argv[1]
toDate = sys.argv[2]
outputFormat = sys.argv[3]

#Interpolation function
def InterpolateResultsFromCentral(CentralResponseFromRequest, TimeStep):
    #Get first start of results received 
    PreviousPowerSegment = CentralResponseFromRequest[0]['start']
    NumberOfInstance = len(CentralResponseFromRequest)

    #Search missing data to feed it
    i = 1
    while (i<NumberOfInstance):
        if(not(CentralResponseFromRequest[i]['start'] == (PreviousPowerSegment + TimeStep))):     
            CentralResponseInterpolation = {
                "start": PreviousPowerSegment + TimeStep,
                 "end": PreviousPowerSegment + TimeStep*2,
                 "power": ((CentralResponseFromRequest[i-1]["power"] + CentralResponseFromRequest[i]["power"])/2)
                 }
            CentralResponseFromRequest.append(CentralResponseInterpolation)
        PreviousPowerSegment = CentralResponseFromRequest[i]["start"]
        i+=1

    CentralResultsInterpolated = sorted(CentralResponseFromRequest, key=operator.itemgetter("start"))
    return CentralResultsInterpolated

#Get results from Hawes
try:
    HawesResponseFromRequest = requests.get('https://interview.beta.bcmenergy.fr/hawes?from=' + fromDate + '&to=' + toDate)
except:
    print("Error during request of Hawes data :" + HawesResponseFromRequest)

#Convert into list
HawesResponse = json.loads(HawesResponseFromRequest.text)

#Interpolation for missing data
HawesResultsInterpolated = InterpolateResultsFromCentral(HawesResponse, 900)

"""
#Display Hawes's resuls
print("Hawes's results :")
for iteration in HawesResultsInterpolated:
    print(iteration)
print('----------')
"""

#Get results from Barnsley
try:
    BarnsleyResponseFromRequest = requests.get('https://interview.beta.bcmenergy.fr/barnsley?from=' + fromDate + '&to=' + toDate)
except:
    print("Error during request of Barnsley data :" + BarnsleyResponseFromRequest)

#Convert into list
BarnsleyResponse = json.loads(BarnsleyResponseFromRequest.text)

#Convert format of Barnsley's results
i = 0
while (i<len(BarnsleyResponse)):
    for iteration in BarnsleyResponse:
        iteration["start"] = iteration.pop("start_time")
        iteration["end"] = iteration.pop("end_time")
        iteration["power"] = iteration.pop("value")
        i+=1

#Interpolation for missing data
BarnsleyResultsInterpolated = InterpolateResultsFromCentral(BarnsleyResponse, 900)

"""
#Display Barnsley's results
print("Barnsley's results :")
for iteration in BarnsleyResultsInterpolated:
    print (iteration)
print('----------')
"""

#Get results from Hounslow
try:
    HounslowResponseFromRequest = requests.get('https://interview.beta.bcmenergy.fr/hounslow?from=' + fromDate + '&to=' + toDate)
except:
    print("Error during request of Hounslow data :" + HounslowResponseFromRequest)

#Convert format of Hounslow's results in json
HounslowFormat = HounslowResponseFromRequest.text
HounslowFormat = HounslowFormat.replace("\n",",")
HounslowFormat = HounslowFormat.split(",")

HounslowList = []
HounslowResponse = []
HounslowDict = {}
i = 3
while (i<(len(HounslowFormat))):
    HounslowList = [HounslowFormat[i],HounslowFormat[i+1],HounslowFormat[i+2]]
    HounslowDict= {
        "start": int(HounslowList[0]),
        "end": int(HounslowList[1]),
        "power": int(HounslowList[2])
        }
    HounslowResponse.append(HounslowDict)
    i+=3

#Interpolation for missing data
HounslowResultsInterpolated = InterpolateResultsFromCentral(HounslowResponse, 900)

"""
#Display Barnsley's results
print("Hounslow's results :")
for iteration in HounslowResultsInterpolated:
    print (iteration)
print('----------')
"""

#Concatenate all results in one list
AllCentralResults = HawesResultsInterpolated
i = 0
while (i<len(AllCentralResults)):
    for iteration in AllCentralResults:
        iteration["power"] = HawesResultsInterpolated[i]["power"] + BarnsleyResultsInterpolated[i]["power"] + HounslowResultsInterpolated[i]["power"]
        i+=1

"""
#Display result of concatenation
print("Results of concatenation :")
for iteration in AllCentralResults:
    print(iteration)
"""

#Save results in file depending on format
if(outputFormat=="json"):
    with open('CentralsConcatenation.json','w') as jsonFile:
        json.dump(AllCentralResults, jsonFile)
#else:
   #save in csv file 

