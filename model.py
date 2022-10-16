import bisect
import pickle
import math
import streamlit as st
from datetime import time

weights = pickle.load(open('weights.pkl','rb'))
hists = pickle.load(open('hists.pkl','rb'))
baseweights = pickle.load(open('baseweights.pkl','rb'))

weekday = [ 'Monday','Tuesday','Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

source = {'In Store':'IN_STORE', 'Online':'ONLINE', 'API':'API'}

payment_mode = { 'In Store' : ['Contactless', 'Keyed In', 'Swiped', 'EMV Chip In', 'Pre Authenticated'],
                 'Online' :   ['Google Pay', 'Apple Pay', 'Online', 'Saved Card'],
                 'API' :      ['Apple Pay', 'Saved Card', 'Online', 'Pre Authenticated' ]}

payment_mode_map = {'Apple Pay':'APPLE_PAY_CNP','Google Pay':'GOOGLE_PAY_CNP', 'Keyed In':'KEYED',
                    'Online':'ONLINE', 'Swiped':'SWIPED','Pre Authenticated':'PRE_AUTHED', 'EMV Chip In':'EMV_CHIP_SIGN',
                    'Saved Card':'SAVED_CARD','Contactless':'CONTACTLESS'}

state = {   'Alaska':'Pacific', 'Alabama':'East South Central', 'Arkansas':'West South Central', 'Arizona':'Mountain',
            'California':'Pacific', 'Colorado':'Mountain', 'Connecticut':'New England', 'District of Columbia':'South Atlantic',
            'Delaware':'South Atlantic', 'Florida':'South Atlantic', 'Georgia':'South Atlantic', 'Hawaii':'Pacific', 'Iowa':'West North Central',
            'Idaho':'Mountain', 'Illinois':'East North Central', 'Indiana':'East North Central', 'Kansas':'West North Central',
            'Kentucky':'East South Central', 'Louisiana':'West South Central', 'Massachusetts':'New England', 'Maryland':'South Atlantic',
            'Maine':'New England', 'Michigan':'East North Central', 'Minnesota':'West North Central', 'Missouri':'West North Central',
            'Mississippi':'East South Central', 'Montana':'Mountain', 'North Carolina':'South Atlantic', 'North Dakota':'West North Central',
            'Nebraska':'West North Central', 'New Hampshire':'New England', 'New Jersey':'Middle Atlantic', 'New Mexico':'Mountain',
            'Nevada':'Mountain','New York':'Middle Atlantic', 'Ohio':'East North Central', 'Oklahoma':'West South Central',
            'Oregon':'Pacific', 'Pennsylvania':'Middle Atlantic', 'Rhode Island':'New England', 'South Carolina':'South Atlantic',
            'South Dakota':'West North Central', 'Tennessee':'East South Central', 'Texas':'West South Central','Utah':'Mountain',
            'Virginia':'South Atlantic', 'Vermont':'New England', 'Washington':'Pacific', 'Wisconsin':'East North Central',
            'West Virginia':'South Atlantic', 'Wyoming':'Mountain'}


def get_tipratio(a, b):
    if b==0:
        return 0
    else:
        return a/b

def get_score(val, col):
    bucket = hists[col]
    t = bisect.bisect_right(bucket, val) - 1
    if t >= len(bucket)-1 :
        t = -1
    if w_key in weights:
        nobs = weights[w_key][0][0]
        score = weights[w_key][1][col][t]
        if score == 0:
            score = 1/nobs
    else :
        score = baseweights[col][t]
    score = math.log(1/score)
    return score

st.title('Transaction Anomaly Model Demonstration')
st.subheader('Transaction Attributes')

_state = st.selectbox('Location of the Store', options = state.keys())
_weekday = st.selectbox('Day of Transaction', options = weekday)
_tstype = st.selectbox('Source of Transaction', options = source.keys())
_pm = st.selectbox('Payment Mode', options = payment_mode[_tstype])
_hourofday = st.slider('Time of the Transaction', value=time(0,0))
_amount = st.number_input('Amount of the Order', min_value=0, step =500)
_tip = st.number_input('Tipped Amount on the Order', min_value=0, step =50)
_tipratio = get_tipratio(_tip, _amount)


state_key = state[_state]
source_key = source[_tstype]
pm_key = payment_mode_map[_pm]
w_key = ','.join([_weekday,source_key,pm_key,state_key ])

s1 = get_score(_amount, 'amount')
s2 = get_score(_tip, 'tipAmount')
s3 = get_score(_tipratio, 'tipRatio')
s4 = get_score(_hourofday.hour, 'paidDate_hourOfDay')

out_score = {'Amount': s1, 'Tip Amount': s2, 'Tip Ratio' : s3, 'Transaction Hour' : s4}
anomaly_score1 = max(zip(out_score.values(), out_score.keys()))
anomaly_score2 = math.sqrt(s1*s1 + s2*s2 + s3*s3 +s4*s4)

col1, col2 = st.columns(2)

col1.metric(label="Anomaly Score", value=round(anomaly_score1[0],1), delta=anomaly_score1[1])
col2.metric(label="Norm Anomaly Score", value=round(anomaly_score2,1), delta=anomaly_score1[1])

        