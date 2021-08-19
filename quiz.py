from flask import *
from cacon1 import cassandra_connect
import os
import random
from datetime import datetime,timedelta,date
from flask_mail import *  
from random import * 
import itertools

app = Flask(__name__)

mail = Mail(app)  
  
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465     
app.config["MAIL_USERNAME"] = 'techquiz.nkl@gmail.com'  
app.config['MAIL_PASSWORD'] = 'techquiz@1999'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  
  
mail = Mail(app)  

count=[0]
dammy=[-1]
student=[]
quest_ans=[]
quest_option=[]
quest_append=[]
quest_num=[]
allmails=[]

@app.route('/', methods=['GET','POST'])
def log():
    if request.method=="GET":
        student.clear()
        return render_template("index.html")
    else:
        mail=request.form['mail']
        pas=request.form['pas']

        if mail=="NewUser@gmail.com" and pas=="user123":
            qn=randint(1,9999999999)
            return render_template("quest.html",qn=qn)
        else:
            csession=cassandra_connect()
            csession.execute('USE quiz')
            rows = csession.execute('select * from student where mail=%(mail)s and pas=%(pas)s ALLOW FILTERING',
            {'mail':mail,'pas':pas})
            r=[]
            for row in rows:
                r.append([row.mail,row.pas])
                if row.mail==mail and row.pas==pas:
                    print("Logged iN")
                    student.append(row.mail)
                    student.append(row.name)
                    student.append(row.phone)
                    print(student)
                    
                    csession=cassandra_connect()
                    csession.execute('USE quiz')
                    rows = csession.execute('select * from question')
                    for row in rows:
                        quest_num.append(row.question_number)
                    print(quest_num)
                    print("Dammy : ",dammy)
                    d=int(dammy[0])
                    return render_template("welcome.html",name=student[1],quest=quest_num[d])    
            return "<h2>Invalid password</h2>"
        return "<h2>Invalid-password</h2>"

@app.route('/quest', )
def quest():
    qn=randint(1,9999999999)
    return render_template("quest.html",qn=qn)

@app.route('/score', methods=['GET'])
def display(): 
    csession=cassandra_connect()
    csession.execute('USE quiz')  
    rows = csession.execute('SELECT * FROM score')
    r=[]
    for row in rows:
        r.append([row.mail,row.name,row.phone,row.points])
    r=tuple(r)
    return render_template('qmsg2.html',r=r)


@app.route('/add', methods=['POST'])
def add2():
    qn=request.form['qn']
    quest=request.form['quest']
    op1=request.form['op1']
    op2=request.form['op2']
    op3=request.form['op3']
    ans=request.form['ans']
    csession=cassandra_connect()
    csession.execute('USE quiz')
    csession.execute(
    """
    INSERT INTO question (question_number,question,op1,op2,op3,ans)
    VALUES (%(question_number)s, %(question)s, %(op1)s, %(op2)s,%(op3)s,%(ans)s)
    """,{'question_number':qn,'question':quest,'op1':op1,"op2":op2,"op3":op3,'ans':ans}
    )
    qn=randint(1,9999999999)
    return render_template("quest.html",qn=qn,delmsg="New Question Inserted")

@app.route('/takeqwiz/<quest>')
def takequiz(quest):
    smail=student[0]
    csession=cassandra_connect()
    csession.execute('USE quiz')
    rows = csession.execute('select * from score where mail=%(mail)s  ALLOW FILTERING',
    {'mail':smail})
    r=[]
    for row in rows:
        r.append([row.mail])
        if row.mail==smail:
            return render_template("qmsg.html",message="You already responded to the quiz..! Wait for next!!,.. we will update u through mail")
        

    dammy[0]+=1
    d=int(dammy[0])
    l=len(quest_num)
    if d==l:
        score="Your total score is : "+str(count[0])+" out of "+str(dammy[0])
        return render_template("qmsg.html",msg=score, message2="Ok..👍")
    quest_ans.clear()
    quest_append.clear()
    quest_option.clear()
    n = '0123'
    a = [''.join(i) for i in itertools.permutations(n, 4)]

    i=randint(0,23)
    print(a)
    print(i)
    print(a[i])
    s=a[i]
    ls=list(s)
    n1=int(ls[0])
    n2=int(ls[1])
    n3=int(ls[2])
    n4=int(ls[3])
            
    csession=cassandra_connect()
    csession.execute('USE quiz')
    row2 = csession.execute('select * from question where question_number=%(question_number)s',{'question_number':quest})
    for row in row2:
        quest_append.append(row.question_number)
        quest_append.append(row.question)
        quest_option.append(row.op1)
        quest_option.append(row.op2)
        quest_option.append(row.op3)
        quest_option.append(row.ans)
        quest_ans.append(row.ans)
    print("Quest append :",quest_append)
    print( "quest_option :",quest_option)
    print("quest_num :",quest_num)
    print("student :",student)
    print("quest_ans :",quest_ans)
    print( "quest_option[n2] :",quest_option[n2]) 
    return render_template("questshow.html",qstno=quest_append[0],qus=quest_append[1],c1=quest_option[n1],c2=quest_option[n2],c3=quest_option[n3],c4=quest_option[n4])

@app.route("/ans_varify",methods=['get','post'])
def varify():
    print("Dammy : ",dammy)
    
    d=int(dammy[0])
    ans=request.form['answer']
    if ans==quest_ans[0]:
        count[0]+=1
        return render_template("qmsg.html",msg="Right answer,....🤩🤩🤩",next=quest_num[d],msg2="Next")
    else :
        return render_template("qmsg.html",msg="Wrong answer,....😭😭😭",msg1="Right anwer is "+quest_ans[0],next=quest_num[d],msg2="Next")

@app.route('/create', methods=['GET','POST'])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        name=request.form['name']
        mail=request.form['mail']
        pas=request.form['pas']
        phone=request.form['phone']

        csession=cassandra_connect()
        csession.execute('USE quiz')
        csession.execute(
        """
        INSERT INTO student (mail,name,pas,phone) 
        VALUES (%(mail)s, %(name)s, %(pas)s, %(phone)s)
        """,{'mail':mail,'name':name,'pas':pas,"phone":phone}
        )
        return render_template("index.html")

@app.route('/close', methods=['GET','POST'])
def close():
    
    csession=cassandra_connect()
    csession.execute('USE quiz')

    rows = csession.execute('select * from student')
    for row in rows:
        allmails.append(row.mail)
    
    print(allmails)
    csession.execute(
    """
    Truncate table score
    """
    )

    sendmsg ="Quiz is ready..🥳!! Participate now to get rewards..🤩🤩🤩"
    print(sendmsg)

    msg = Message('Participate',sender = 'techquiz.nkl@gmail.com', recipients = allmails)  
    msg.body = sendmsg
    mail.send(msg)
    qn=randint(1,9999999999)
    return render_template("quest.html",qn=qn,delmsg="Score board for ealier quiz is cleared,... New Score will be updated as participants takes the quiz..")

@app.route('/delete', methods=['GET'])
def delete():
    
    csession=cassandra_connect()
    csession.execute('USE quiz')

    csession.execute(
    """
    Truncate table question
    """
    )
    qn=randint(1,9999999999)
    return render_template("quest.html",qn=qn,delmsg="All Old questions deleted")

@app.route("/updateScore")
def update():
    smail=student[0]
    score=str(count[0])+"/"+str(dammy[0])
    
    
    sid=str(randint(1,9999999999))
    print ("Score = "+score)

    csession=cassandra_connect()
    csession.execute('USE quiz')
    csession.execute(
    """
    INSERT INTO score (id,mail,name,phone,points) 
    VALUES (%(id)s, %(mail)s, %(name)s, %(phone)s, %(points)s)
    """,{'id':sid,'mail':smail,'name':student[1],'phone':student[2],'points':score
    })

    sendmsg ="Your Total score is "+str(count[0])+" out of "+str(dammy[0])
    print(sendmsg)

    msg = Message('Score',sender = 'techquiz.nkl@gmail.com', recipients = [smail])  
    msg.body = sendmsg
    mail.send(msg)
    
    student.clear()
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
