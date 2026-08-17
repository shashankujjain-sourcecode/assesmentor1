import streamlit as st
from assessment.db import init_db, start_attempt, get_attempt, save_answer, set_index, finish_attempt
from assessment.engine import Assessment
from reports.pdf_report import make_report

st.set_page_config(page_title='Career Discovery', page_icon='🎓', layout='wide')
init_db()
if 'attempt' not in st.session_state: st.session_state.attempt=None

st.title('🎓 Career Discovery Assessment')

if st.session_state.attempt is None:
    st.subheader('Student registration')
    with st.form('start'):
        name=st.text_input('Student name')
        code=st.text_input('Student code / roll number')
        school=st.text_input('School')
        cls=st.selectbox('Class',['8','9','10','11','12'])
        ok=st.form_submit_button('Start assessment')
    if ok:
        if not name.strip() or not code.strip(): st.error('Name and student code are required.')
        else:
            st.session_state.attempt=start_attempt(name.strip(),code.strip(),school.strip(),cls)
            st.rerun()
    st.stop()

a=get_attempt(st.session_state.attempt)
if a['status']=='completed':
    st.success('Assessment completed.')
    st.write('Your personalized report is ready.')
    if st.button('Generate detailed PDF report'):
        pdf=make_report(a['id'])
        st.download_button('Download report',pdf,f'career_report_{a["student_code"]}.pdf','application/pdf')
    st.stop()

assessment=Assessment(a)
qs=assessment.questions
i=a['current_index']
q=qs[i]
st.progress(i/len(qs),text=f'Question {i+1} of {len(qs)}')
st.subheader(q['question'])
old=a['answers'].get(q['id'])
choice=st.radio('Select the option that best describes you.',q['options'],index=q['options'].index(old) if old in q['options'] else None,key=q['id'])

c1,c2=st.columns(2)
with c1:
    if i>0 and st.button('← Previous'):
        set_index(a['id'],i-1); st.rerun()
with c2:
    if st.button('Finish assessment' if i==len(qs)-1 else 'Next →',type='primary'):
        if choice is None: st.warning('Please select an answer.')
        else:
            save_answer(a['id'],q['id'],choice)
            if i==len(qs)-1: finish_attempt(a['id'])
            else: set_index(a['id'],i+1)
            st.rerun()
st.caption('Progress is saved after every answer.')
