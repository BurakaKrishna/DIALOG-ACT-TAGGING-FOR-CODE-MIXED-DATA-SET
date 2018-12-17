from __future__ import division #To avoid integer division
from operator import itemgetter
###Training Phase###

with open("train_utterance", "r") as myfile:
    tr_str = myfile.read()

tr_li = tr_str.split()
num_words_train = len(tr_li)


train_li_words = []
train_li_words*= num_words_train

train_li_tags = []
train_li_tags*= num_words_train

file1 = open("train_utterance","r")
f_data = file1.readlines()
for i in range(0,len(f_data)):
        temp_li = f_data[i].strip().split("\t\t")
        train_li_words.append(temp_li[1])
        train_li_tags.append(temp_li[2])

print(train_li_words)
print(train_li_tags)

dict2_tag_follow_tag_ = {}
dict2_word_tag = {}

dict_word_tag_baseline = {}
#Dictionary with word as key and its most frequent tag as value

for i in range(len(f_data)-1):
    outer_key = train_li_tags[i]
    inner_key = train_li_tags[i+1]
    dict2_tag_follow_tag_[outer_key]=dict2_tag_follow_tag_.get(outer_key,{})
    dict2_tag_follow_tag_[outer_key][inner_key] = dict2_tag_follow_tag_[outer_key].get(inner_key,0)
    dict2_tag_follow_tag_[outer_key][inner_key]+=1

    outer_key = train_li_words[i]
    inner_key = train_li_tags[i]
    dict2_word_tag[outer_key]=dict2_word_tag.get(outer_key,{})
    dict2_word_tag[outer_key][inner_key] = dict2_word_tag[outer_key].get(inner_key,0)
    dict2_word_tag[outer_key][inner_key]+=1


dict2_tag_follow_tag_['.'] = dict2_tag_follow_tag_.get('.',{})
dict2_tag_follow_tag_['.'][train_li_tags[0]] = dict2_tag_follow_tag_['.'].get(train_li_tags[0],0)
dict2_tag_follow_tag_['.'][train_li_tags[0]]+=1


last_index = len(f_data)-1

#Accounting for the last word-tag pair
outer_key = train_li_words[last_index]
inner_key = train_li_tags[last_index]
dict2_word_tag[outer_key]=dict2_word_tag.get(outer_key,{})
dict2_word_tag[outer_key][inner_key] = dict2_word_tag[outer_key].get(inner_key,0)
dict2_word_tag[outer_key][inner_key]+=1


"""Converting counts to probabilities in the two nested dictionaries
& also converting the nested dictionaries to outer dictionary with inner sorted lists
"""
for key in dict2_tag_follow_tag_:
    di = dict2_tag_follow_tag_[key]
    s = sum(di.values())
    for innkey in di:
        di[innkey] /= s
    di = di.items()
    di = sorted(di,key=lambda x: x[0])
    dict2_tag_follow_tag_[key] = di

for key in dict2_word_tag:
    di = dict2_word_tag[key]
    dict_word_tag_baseline[key] = max(di, key=di.get)
    s = sum(di.values())
    for innkey in di:
        di[innkey] /= s
    di = di.items()
    di = sorted(di,key=lambda x: x[0])
    dict2_word_tag[key] = di

###Testing Phase###    

with open("test_utterance", "r") as myfile:
    te_str = myfile.read()

te_li = te_str.split()
num_words_test = len(te_li)

test_li_words = ['']
test_li_words*= num_words_test

test_li_tags = ['']
test_li_tags*= num_words_test

output_li = ['']
output_li*= num_words_test

output_li_baseline = ['']
output_li_baseline*= num_words_test

num_errors = 0
num_errors_baseline = 0

file1 = open("test_utterance","r")
f_data = file1.readlines()
for i in range(0,len(f_data)):
    temp_li = f_data[i].strip().split("\t\t")
    test_li_words[i] = temp_li[1]
    test_li_tags[i] = temp_li[2]

    output_li_baseline[i] = dict_word_tag_baseline.get(temp_li[0],'')
    #If unknown word - tag = 'NNP'
    if output_li_baseline[i]=='':
        output_li_baseline[i]='ASSERT'
        

    if output_li_baseline[i]!=test_li_tags[i]:
        num_errors_baseline+=1

    
    if i==0:    #Accounting for the 1st word in the test document for the Viterbi
        di_transition_probs = dict2_tag_follow_tag_['.']
    else:
        di_transition_probs = dict2_tag_follow_tag_[output_li[i-1]]
        
    di_emission_probs = dict2_word_tag.get(test_li_words[i],'')

    #If unknown word  - tag = 'NNP'
    if di_emission_probs=='':
        output_li[i]='ASSERT'
        
    else:
        max_prod_prob = 0
        counter_trans = 0
        counter_emis =0
        prod_prob = 0
        while counter_trans < len(di_transition_probs) and counter_emis < len(di_emission_probs):
            tag_tr = di_transition_probs[counter_trans][0]
            tag_em = di_emission_probs[counter_emis][0]
            if tag_tr < tag_em:
                counter_trans+=1
            elif tag_tr > tag_em:
                counter_emis+=1
            else:
                prod_prob = di_transition_probs[counter_trans][1] * di_emission_probs[counter_emis][1]
                if prod_prob > max_prod_prob:
                    max_prod_prob = prod_prob
                    output_li[i] = tag_tr
                    #print "i=",i," and output=",output_li[i]
                counter_trans+=1
                counter_emis+=1    
    

    if output_li[i]=='': #In case there are no matching entries between the transition tags and emission tags, we choose the most frequent emission tag
        output_li[i] = max(di_emission_probs,key=itemgetter(1))[0]  
        
    if output_li[i]!=test_li_tags[i]:
        num_errors+=1

                    
print "Fraction of errors (Baseline) :",(num_errors_baseline/num_words_test)
print "Fraction of errors (Viterbi):",(num_errors/num_words_test)

#print "Tags suggested by Baseline Algorithm:", output_li_baseline

#print "Tags suggested by Viterbi Algorithm:", output_li

#print "Correct tags:",test_li_tags

bcount=0
bcount1=0

vcount=0
vcount1=0


test_tags = [x for x in test_li_tags if x]
output_tags = [x for x in output_li if x]

for i in range(0,len(test_tags)):
    if(output_li_baseline[i]==test_li_tags[i]):
        bcount+=1
    else:
        bcount1+=1
    if(output_li[i]==test_li_tags[i]):
        vcount+=1
    else:
        vcount1+=1
       
print(test_tags)
print(output_tags)
print(len(test_tags))
print(bcount,bcount1)
print(vcount, vcount1)
        





